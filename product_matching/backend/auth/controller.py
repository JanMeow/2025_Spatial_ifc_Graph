from fastapi import APIRouter, HTTPException
from auth.service import get_access_token
from auth.model import LoginRequest
# =========================================================================================
#  Auth Controller
# =========================================================================================
router = APIRouter(prefix="/auth")
@router.post("/login")
async def login(platform_api: str, request: LoginRequest):
    return get_access_token(request.email, request.password)