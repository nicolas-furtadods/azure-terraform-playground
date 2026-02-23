import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import modules
from .modules.helpers import helpers
from .routers.example import router as examplerouter
from .routers.health import health

load_dotenv()

# Import sub-folder APIs
# https://fastapi.tiangolo.com/tutorial/bigger-applications/#the-main-fastapi

# Do not forget to add router
# from .routers.example import router as example

# Declare the main API
app = FastAPI(
    title="FastAPI Code",
    description="A FastAPI template for Azure Terraform Playground",
    version="1.0.0",
)

# Include sub-folder APIs
app.include_router(health.router)
app.include_router(examplerouter.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        {
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
        status_code=exc.status_code,
        media_type="application/json",
    )
