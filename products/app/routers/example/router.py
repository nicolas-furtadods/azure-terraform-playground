from fastapi import APIRouter, FastAPI, HTTPException, Security, status

from ...models.example import models
from ...modules.auth.azure_auth import (DEFAULT_REQUIRED_SCOPES,
                                        require_azure_token)
from ...modules.helpers import helpers

router = APIRouter(
    prefix="/example",
    tags=["example"],
    responses={404: {"description": "Not found"}},
    dependencies=[
        Security(
            require_azure_token,
            scopes=DEFAULT_REQUIRED_SCOPES)],
)


@router.get("", summary="Get all items")
async def read_items() -> list[models.Item]:
    """Get all items"""
    return [
        models.Item(id=1, name="Item 1", tags=[]),
        models.Item(id=2, name="Item 2", tags=[]),
    ]


@router.post(
    "",
    summary="Create an item",
    status_code=status.HTTP_201_CREATED,
    response_description="The created item",
)
async def create_item(item: models.Item) -> models.Item:
    """Create an item"""
    return item
