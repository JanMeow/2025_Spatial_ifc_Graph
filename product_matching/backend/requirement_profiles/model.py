from pydantic import BaseModel
from typing import Optional, Dict, List, Any, Literal
# =========================================================================================
#  Schema: Requirement Profile Request
# =========================================================================================
class RequirementProfileRequest(BaseModel):
    product: str = "Aussenwand 1.1"
    tThresh: float = 400
    pThresh: float = 350
    uThresh: float = 0.2
    pTol:float = 10
    tTol: float = 20
    uTol: float = 0.03
    tThreshOp: Literal["==", "~=", "<", "<=", ">", ">="] = "~="
    pThreshOp: Literal["==", "~=", "<", "<=", ">", ">="] = "<="
    uThreshOp: Literal["==", "~=", "<", "<=", ">", ">="] = "<="
    sampling: Optional[str] = None
    preFilter: Optional[Dict[str, Optional[List[int]]]] = None
# =========================================================================================
#  Schema: Requirement Profile Response
# =========================================================================================
class RequirementProfileResponse(BaseModel):
    meets_req: Dict[str, List[Dict[str, Any]]] = {}
    meets_req_with_tol: Dict[str, List[Dict[str, Any]]] = {}
    fails_req: Dict[str, List[Dict[str, Any]]] = {}
# =========================================================================================
#  Domain: Product Combination
# =========================================================================================
class Weights(BaseModel):
    thickness: int = 5
    price: int = 1
    u_value: int = 1
    acoustic: Optional[int] = None
    fire_rating: Optional[int] = None

factors = ["thickness", "price", "U_value", "fire_rating", "acoustics"]
