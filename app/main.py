## === app/main.py ===

from fastapi import FastAPI
from app.api.v1 import v1_router
from app.core.middleware import setup_middlewares
from app.config import settings
from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title=settings.project_name, debug=settings.debug)



# app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


setup_middlewares(app)

# Include routers
app.include_router(v1_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body.decode() if isinstance(exc.body, bytes) else exc.body
        }
    )

@app.on_event("startup")
async def startup():
    # Example: Check DB connection or preload models
    # from app.settings import settings
    print(f"Starting up  {settings.project_name} in {settings.environment} mode...")