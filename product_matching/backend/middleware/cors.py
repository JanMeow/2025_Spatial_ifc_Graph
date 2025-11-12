from fastapi import FastAPI
from middleware.settings import Settings
from fastapi.middleware.cors import CORSMiddleware
from middleware.logging import add_logging_middleware
# =========================================================================================
#  CORS Middleware
# =========================================================================================
def add_cors_middleware(app:FastAPI, settings:Settings, add_logging:bool = True):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=settings.allow_credentials,
        allow_methods=settings.allow_methods,
        allow_headers=settings.allow_headers,
    )
    if add_logging:
        add_logging_middleware(app)
