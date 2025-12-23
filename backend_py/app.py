import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="GeoSmart Multi-Agent Backend (Python)", version="1.0.0")

# CORS configuration (allow all origins for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from .routers import complaints
app.include_router(complaints.router, prefix="/api")

# Serve static files (uploads)
from fastapi.staticfiles import StaticFiles
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": os.getenv("TZ", "") or "",
        "service": "GeoSmart Multi-Agent Backend (Python)"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "GeoSmart Multi-Agent Grievance System API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "complaints": {
                "create": "POST /api/complaints",
                "list": "GET /api/complaints",
                "get": "GET /api/complaints/:id",
                "update": "PATCH /api/complaints/:id"
            }
        },
        "documentation": "See README.md for API details"
    }

# Run the server (only when executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 3000)))
