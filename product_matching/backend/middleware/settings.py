from pydantic_settings import BaseSettings
# =========================================================================================
#  Settings
# =========================================================================================
class Settings(BaseSettings):
    allow_origins: list[str] = ["*"]  # In production, specify your frontend URL
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
