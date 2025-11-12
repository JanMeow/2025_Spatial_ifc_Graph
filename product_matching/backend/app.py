import numpy as np
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import strawberry
from strawberry.fastapi import GraphQLRouter
from schema import Query, Mutation
from dotenv import load_dotenv
import os
from middleware.cors import add_cors_middleware
from middleware.settings import Settings
from buildups.controller import router as buildups_router
from lignum.controller import router as lignum_router
from requirement_profiles.controller import router as requirementprofile_router
# =========================================================================================
#  Load environment variables
# =========================================================================================
load_dotenv()
PLATFORM_API = os.getenv("PLATFORM_API")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TENANT_SLUG = os.getenv("TENANT_SLUG")
# =========================================================================================
#  GraphQL Schema
# =========================================================================================
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
# =========================================================================================
#  FastAPI app
# =========================================================================================
app = FastAPI(title="Product Performance API", description="API for filtering and analyzing product performance data", version="1.0.0")
# =========================================================================================
#  Exception Handlers
# =========================================================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for validation errors to provide better error messages"""
    errors = []
    for error in exc.errors():
        error_detail = {
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        if "input" in error:
            error_detail["received_value"] = error["input"]
        errors.append(error_detail)
    
    # Print to console for debugging
    print("=" * 80)
    print("VALIDATION ERROR OCCURRED")
    print("=" * 80)
    print(f"Errors: {errors}")
    print("=" * 80)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation Error",
            "errors": errors
        },
    )
# =========================================================================================
#  CORS middleware
# =========================================================================================
add_cors_middleware(app, Settings(), add_logging=True)
# =========================================================================================
#  Include routers
# =========================================================================================
API_PREFIX = "/api/v1"
app.include_router(graphql_app, prefix="/graphql")
app.include_router(buildups_router, prefix=f"{API_PREFIX}/buildups")
app.include_router(lignum_router, prefix=f"{API_PREFIX}/lignum")
app.include_router(requirementprofile_router, prefix=f"{API_PREFIX}/requirement_profiles")
# =========================================================================================
#  API Endpoints
# =========================================================================================
# ====================================
# Root & Health
# ====================================
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Product Performance API",
        "version": "1.0.0",
        "endpoints": {
            "/api/v1/health": "Health check endpoint",
            "/api/v1/products": "Get all available products",
            "/api/v1/products/{product_type}": "Get products by type (e.g., Aussenwand, Innenwand, Decke)",
                "/api/v1/products/{product_type}/{product_name}": "Get specific product details",
                "/api/v1/products/{product_type}/{product_name}/layers": "Get layers for a specific product",
            "/api/v1/lignum/{product_type}/{product_name}": "Get Lignum database data for a product",
            "/api/v1/requirement_profiles/apply": "Apply requirement profile filter (POST)"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }
@app.get("/api/v1/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
@app.get("/api/v1/metrics")
def get_metrics():
    """Get metrics of the application for Prometheus"""
    return {"metrics": {"request_count": 0, "request_time": 0}}
# ====================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,  # Auto-reload on file changes
        reload_dirs=["."],  # Watch current directory
        reload_excludes=["*.pyc", "__pycache__", "venv/*"],  # Exclude these from watching
        log_level="info",  # More detailed logging
        access_log=True,  # Show access logs
    )