from fastapi import FastAPI

app = FastAPI(
    title="My FastAPI Application",
    description="Personal AI platform for various tasks and services.",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "private-ai-platform",
        "version": "0.1.0",
    }