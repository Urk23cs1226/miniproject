"""FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .api.routes import router

# Resolve frontend path relative to THIS file
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_BACKEND_DIR)
FRONTEND_DIR = os.path.join(_PROJECT_DIR, "frontend")

print(f"[CodeIntel] Backend dir : {_BACKEND_DIR}")
print(f"[CodeIntel] Frontend dir: {FRONTEND_DIR}")
print(f"[CodeIntel] Frontend exists: {os.path.exists(FRONTEND_DIR)}")
print(f"[CodeIntel] index.html exists: {os.path.exists(os.path.join(FRONTEND_DIR, 'index.html'))}")

app = FastAPI(
    title="AI Code Analysis System",
    description="AI-powered source code creativity and analysis using Deep Neural Networks",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def serve_frontend():
    """Serve the main dashboard HTML."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {"message": "AI Code Analysis System API", "docs": "/docs", "frontend_dir": FRONTEND_DIR, "exists": os.path.exists(FRONTEND_DIR)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# Mount static files AFTER route definitions so they don't shadow routes
_css_dir = os.path.join(FRONTEND_DIR, "css")
_js_dir = os.path.join(FRONTEND_DIR, "js")
if os.path.exists(_css_dir):
    app.mount("/css", StaticFiles(directory=_css_dir), name="css")
    print(f"[CodeIntel] Mounted /css -> {_css_dir}")
if os.path.exists(_js_dir):
    app.mount("/js", StaticFiles(directory=_js_dir), name="js")
    print(f"[CodeIntel] Mounted /js -> {_js_dir}")
