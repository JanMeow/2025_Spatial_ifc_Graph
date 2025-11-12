import requests
from auth.model import LoginRequest
from typing import Annotated
from fastapi import Depends
# =========================================================================================
#  Dokwood Platform login Service
# =========================================================================================
def get_access_token(platform_api: str, login_input: LoginRequest) -> str:
    query = "mutation LoginOp($loginInput: LoginInputDto!) { login(loginInput: $loginInput) { access_token } }"
    payload = {
        "query": query,
        "variables": {"loginInput": login_input},
        "operationName": "LoginOp"
    }
    try:
        response = requests.post(platform_api,json =payload)
        platform_access_token = response.json()["data"]["login"]["access_token"]
    except Exception as e:
        raise Exception(f"Error logging in: {e}")
    return platform_access_token
def verify_access_token(platform_api: str, access_token: str) -> bool:
    query = "mutation VerifyAccessTokenOp($accessToken: String!) { verifyAccessToken(accessToken: $accessToken) { isValid } }"
    payload = {
        "query": query,
        "variables": {"accessToken": access_token},
        "operationName": "VerifyAccessTokenOp"
    }
    try:
        response = requests.post(platform_api,json =payload)
        return response.json()["data"]["verifyAccessToken"]["isValid"]
    except Exception as e:
        raise Exception(f"Error verifying access token: {e}")

# =========================================================================================
#  Access Dependency
# =========================================================================================
AccessDep = Annotated[str, Depends(get_access_token)]
