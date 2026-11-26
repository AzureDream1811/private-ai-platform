from fastapi import FastAPI

from backend.app.modules.aiservices.router import router as service_router
from backend.app.modules.auth.router import router as auth_router

app = FastAPI(
    title="My FastAPI Application",
    description="Personal AI platform for various tasks and services.",
    version="0.1.0",
)

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
