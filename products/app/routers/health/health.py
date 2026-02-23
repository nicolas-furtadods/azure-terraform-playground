import json, os
from fastapi import APIRouter, FastAPI, HTTPException, status

from ...modules.helpers import helpers

from ...models.health import health

router = APIRouter(
    prefix="/health", 
    tags=["health"]
    # responses={404: {"description": "Not found"}},
)

@router.get(
  "",
  summary="Get the health status of the application",
  response_description="The health status of the application",
  status_code=status.HTTP_200_OK,
  response_model=health.HealthCheck
)
async def get_health_status() -> health.HealthCheck:
    """Get the health status of the application"""
    return health.HealthCheck(
        status="healthy",
    )