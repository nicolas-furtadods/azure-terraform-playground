# FastAPI Azure AD Authentication

This API uses Microsoft Entra ID (Azure AD) **client credentials** tokens.

## Required environment variables

- `AZURE_TENANT_ID`: Tenant GUID (or `common` for multi-tenant)
- `AZURE_API_CLIENT_ID` (or `AZURE_CLIENT_ID`): API app registration client ID (audience)

## Optional environment variables

- `AZURE_TOKEN_URL`: Token endpoint override (default: `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token`)
- `AZURE_OPENID_CONFIG_URL`: OpenID metadata URL override
- `AZURE_REQUIRED_SCOPES`: Comma-separated scopes to enforce (also shown as default Swagger scopes)
- `AZURE_REQUIRED_APP_ROLES`: Comma-separated app roles required from `roles` claim
- `AZURE_ALLOWED_CLIENT_APP_IDS`: Comma-separated calling app IDs allowed (`azp`/`appid` claim)
- `AZURE_SWAGGER_CLIENT_ID`: Optional prefilled Swagger OAuth client ID
- `AZURE_SWAGGER_CLIENT_SECRET`: Optional prefilled Swagger OAuth client secret

## What gets validated

- JWT signature against Entra ID JWKS
- `iss` (issuer) and `aud` (API client ID)
- Required scopes (`scp`/`scope`) when configured
- Required app roles (`roles`) when configured
- Optional allowed caller app IDs (`azp`/`appid`)

## Swagger usage

1. Open `/docs`
2. Click **Authorize**
3. Enter client ID, client secret, and scope(s)
4. Acquire token via client credentials and call protected endpoints

`/health` remains public and `/example` endpoints require a valid token.
