from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, products  # Make sure products is imported
from app.core.config import settings

app = FastAPI(
    title="Lylux Product Configurator API",
    description="FastAPI backend for Lylux lighting product configurator",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(products.router, prefix="/api/products", tags=["products"])  # This line

@app.get("/")
async def root():
    return {"message": "Lylux Product Configurator API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test-supabase-import")
async def test_supabase_import():
    try:
        from app.services.supabase_client import supabase
        return {"status": "success", "message": "Supabase client imported successfully"}
    except Exception as e:
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}