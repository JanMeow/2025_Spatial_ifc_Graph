from fastapi import Request
from fastapi import FastAPI
import time
import logging
# =========================================================================================
#  Logging Middleware
# =========================================================================================
logger = logging.getLogger("backend")
def add_logging_middleware(app:FastAPI):
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        logger.info(f"Request received for {request.url.path}")
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        logger.info(f"Time taken for {request.url.path}: {end_time - start_time} seconds")
        logger.info(f"Response status code: {response.status_code}")
        return response