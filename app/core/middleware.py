from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.core.logger import logger

def setup_middlewares(app: FastAPI):
    # In production
    if settings.environment == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["yourdomain.com"]
        )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Logging middleware
    app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)

async def log_requests(request: Request, call_next):
    """
    Middleware to log all requests and responses.
    """
    logger.info(f"Request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(
            f"Response: {request.method} {request.url} "
            f"Status: {response.status_code}"
        )
        return response
    except Exception as e:
        logger.exception(f"Error processing request: {request.method} {request.url}")
        raise e