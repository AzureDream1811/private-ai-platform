from fastapi import FastAPI

from backend.app.core.exception_handlers import register_exception_handlers
from backend.app.modules.ai_service.router import router as service_router
from backend.app.modules.auth.router import router as auth_router

app = FastAPI(
    title="My FastAPI Application",
    description="Personal AI platform for various tasks and services.",
    version="0.1.0",
)
register_exception_handlers(app)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(
    service_router,
    prefix="/api/v1/services",
    tags=["services"],
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "private-ai-platform",
        "version": "0.1.0",
    }
