import os
import time
from dataclasses import dataclass

import jwt
import requests
from fastapi import Depends, HTTPException, Security, status
from fastapi.openapi.models import OAuthFlowClientCredentials, OAuthFlows
from fastapi.security import OAuth2, SecurityScopes
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request


def _parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class AzureAuthSettings:
    tenant_id: str
    audience: str
    token_url: str
    openid_config_url: str
    required_scopes: list[str]
    required_app_roles: list[str]
    allowed_client_app_ids: list[str]
    swagger_client_id: str | None
    swagger_client_secret: str | None


def get_auth_settings() -> AzureAuthSettings:
    tenant_id = os.getenv("AZURE_TENANT_ID", "common")
    audience = os.getenv("AZURE_API_CLIENT_ID") or os.getenv(
        "AZURE_CLIENT_ID", "")
    print(
        f"Using AzureAuthSettings with tenant_id={tenant_id}, audience={audience}")
    token_url = os.getenv(
        "AZURE_TOKEN_URL",
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
    )
    openid_config_url = os.getenv(
        "AZURE_OPENID_CONFIG_URL",
        f"https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration",
    )

    return AzureAuthSettings(
        tenant_id=tenant_id,
        audience=audience,
        token_url=token_url,
        openid_config_url=openid_config_url,
        required_scopes=_parse_csv(os.getenv("AZURE_REQUIRED_SCOPES")),
        required_app_roles=_parse_csv(os.getenv("AZURE_REQUIRED_APP_ROLES")),
        allowed_client_app_ids=_parse_csv(
            os.getenv("AZURE_ALLOWED_CLIENT_APP_IDS")),
        swagger_client_id=os.getenv("AZURE_SWAGGER_CLIENT_ID"),
        swagger_client_secret=os.getenv("AZURE_SWAGGER_CLIENT_SECRET"),
    )


SETTINGS = get_auth_settings()
DEFAULT_REQUIRED_SCOPES = SETTINGS.required_scopes


def _scope_map(scopes: list[str]) -> dict[str, str]:
    return {scope: f"Required scope: {scope}" for scope in scopes}


class OAuth2ClientCredentialsBearer(OAuth2):
    def __init__(
        self,
        token_url: str,
        scopes: dict[str, str] | None = None,
        scheme_name: str | None = None,
        auto_error: bool = True,
    ):
        if scopes is None:
            scopes = {}

        flows = OAuthFlows(
            clientCredentials=OAuthFlowClientCredentials(
                tokenUrl=token_url, scopes=scopes
            )
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        return token


oauth2_scheme = OAuth2ClientCredentialsBearer(
    token_url=SETTINGS.token_url,
    scopes=_scope_map(SETTINGS.required_scopes),
    scheme_name="AzureADClientCredentials",
)


_jwks_client: jwt.PyJWKClient | None = None
_metadata_cache: dict[str, str | float] = {}
_metadata_ttl_seconds = 3600


def _get_openid_metadata() -> dict:
    now = time.time()
    cached_at = _metadata_cache.get("cached_at")
    if cached_at and (now - float(cached_at) < _metadata_ttl_seconds):
        return {
            "issuer": _metadata_cache["issuer"],
            "jwks_uri": _metadata_cache["jwks_uri"],
        }

    response = requests.get(SETTINGS.openid_config_url, timeout=10)
    response.raise_for_status()
    metadata = response.json()
    issuer = metadata["issuer"]
    jwks_uri = metadata["jwks_uri"]

    _metadata_cache["cached_at"] = now
    _metadata_cache["issuer"] = issuer
    _metadata_cache["jwks_uri"] = jwks_uri
    return metadata


def _get_jwks_client() -> jwt.PyJWKClient:
    global _jwks_client
    if _jwks_client is not None:
        return _jwks_client

    metadata = _get_openid_metadata()
    _jwks_client = jwt.PyJWKClient(str(metadata["jwks_uri"]))
    return _jwks_client


def _has_required_scopes(claims: dict, required_scopes: list[str]) -> bool:
    print(
        f"Validating required scopes. Required: {required_scopes}, Token claims: {claims}"
    )
    if not required_scopes:
        return True

    token_scopes_raw = claims.get("scp") or claims.get("scope") or ""
    token_scopes = set(str(token_scopes_raw).split())
    return set(required_scopes).issubset(token_scopes)


def _has_required_roles(claims: dict, required_roles: list[str]) -> bool:
    print(
        f"Validating required app roles. Required: {required_roles}, Token claims: {claims}"
    )
    if not required_roles:
        return True

    roles_claim = claims.get("roles", [])
    if isinstance(roles_claim, str):
        token_roles = {roles_claim}
    else:
        token_roles = set(roles_claim)

    return set(required_roles).issubset(token_roles)


def _validate_allowed_client_app(claims: dict) -> bool:
    if not SETTINGS.allowed_client_app_ids:
        return True

    client_app_id = claims.get("azp") or claims.get("appid")
    return client_app_id in SETTINGS.allowed_client_app_ids


def _build_www_authenticate_value(required_scopes: list[str]) -> str:
    if not required_scopes:
        return "Bearer"
    return f'Bearer scope="{" ".join(required_scopes)}"'


def _decode_token(token: str) -> dict:
    if not SETTINGS.audience:
        raise ValueError(
            "AZURE_API_CLIENT_ID or AZURE_CLIENT_ID must be configured.")

    metadata = _get_openid_metadata()
    jwks_client = _get_jwks_client()

    # Security issue I should address: The get_signing_key_from_jwt method fetches the JWKS keys and finds the matching key based on the "kid" in the token header. However, if an attacker can manipulate the token header to specify a "kid" that points to a malicious key, they could potentially forge tokens. To mitigate this, I should implement additional checks to ensure that the "kid" corresponds to a trusted key and consider caching the JWKS keys to prevent frequent fetching.
    # TO DO
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    print(f"Decoding token with signing key kid={signing_key.key_id}")
    print(
        f"Metadata issuer={metadata['issuer']}, jwks_uri={metadata['jwks_uri']}")
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=SETTINGS.audience,
        # (Update 2025): The property is now named requestedAccessTokenVersion in the new "Microsoft Graph App Manifest". https://learn.microsoft.com/en-us/entra/identity-platform/azure-active-directory-graph-app-manifest-deprecation#attribute-differences-between-azure-ad-graph-and-microsoft-graph-formats. The default value is still null and needs to be changed to 2.
        # issuer=metadata["issuer"],
        options={
            "verify_signature": True,
            "verify_aud": True,
            "verify_iss": True},
    )
    return claims


async def require_azure_token(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> dict:
    required_scopes = security_scopes.scopes or SETTINGS.required_scopes

    try:
        claims = _decode_token(token)
    except Exception as ex:
        print(f"Token validation error: {ex}")
        if isinstance(ex, jwt.ExpiredSignatureError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token has expired. Please obtain a new token against Microsoft Identity Platform.",
                headers={
                    "WWW-Authenticate": _build_www_authenticate_value(required_scopes)
                },
            ) from ex
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={
                "WWW-Authenticate": _build_www_authenticate_value(required_scopes)
            },
        ) from ex

    # Not used at the moment but we can use it to filter the client
    # application that can access the API. For example, we can allow only a
    # specific client application to access the API by checking the "azp" or
    # "appid" claim in the token
    if not _validate_allowed_client_app(claims):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized client application",
        )

    # Scoppe is not in the claims
    # if not _has_required_scopes(claims, required_scopes):
    #    raise HTTPException(
    #        status_code=status.HTTP_403_FORBIDDEN,
    #        detail="Missing required scope",
    #    )

    # Verify that the user have the required app role to access the API.
    # `azure.read` is at least required.
    if not _has_required_roles(claims, SETTINGS.required_app_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing required App role for API access.",
        )

    return claims


def get_swagger_ui_init_oauth() -> dict:
    config: dict[str, str | list[str]] = {}
    if SETTINGS.swagger_client_id:
        config["clientId"] = SETTINGS.swagger_client_id
    if SETTINGS.swagger_client_secret:
        config["clientSecret"] = SETTINGS.swagger_client_secret
    if SETTINGS.required_scopes:
        config["scopes"] = SETTINGS.required_scopes
    return config


def build_auth_dependency(scopes: list[str] | None = None):
    scopes = scopes or SETTINGS.required_scopes
    return Security(require_azure_token, scopes=scopes)
