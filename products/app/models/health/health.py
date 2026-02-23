from pydantic import BaseModel


class HealthCheck(BaseModel):
    """
    HealthCheck model for API health status."""

    status: str
