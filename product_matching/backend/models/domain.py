import numpy as np
import strawberry
from typing import Optional, List
from pydantic import BaseModel
from dataclasses import dataclass
# =========================================================================================
#  Domain Models data definitions
# =========================================================================================
@strawberry.type
class Props:
    thickness: int
    price: float
    u_value: float
    fire_rating: float
    acoustic: float
    lambda_value: float

@strawberry.type
class Layer:
    id: strawberry.ID
    name: str
    props: Optional[Props] = None

@strawberry.type
class BuildUp:
    id: strawberry.ID
    name: str
    type:str
    description: Optional[str] = None
    layers: Optional[List[Layer]] = None
    props: Optional[Props] = None

@strawberry.type
class RequirementProfile:
    id: strawberry.ID
    name: str
    type:str
    description: Optional[str] = None
    props: Optional[Props] = None
    targets: Optional[List[BuildUp]] = None

@strawberry.type
class Product:
    id: strawberry.ID
    name: str
    type:str
    description: Optional[str] = None
    props: Optional[Props] = None
    layers: Optional[List[Layer]] = None
    build_ups: Optional[List[BuildUp]] = None

@strawberry.type
class ProductGroup:
    id: strawberry.ID
    name: str
    requirement_profiles: Optional[List[RequirementProfile]] = None
    description: Optional[str] = None
    products: Optional[List[Product]] = None