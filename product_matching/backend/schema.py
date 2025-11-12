import strawberry
from typing import List, Optional
# =========================================================================================
#  Output Types
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
    description: Optional[str] = None
    props: Optional[Props] = None
    target: Optional[List[BuildUp]] = None
# =========================================================================================
#  Helper Functions
# =========================================================================================
def get_build_ups(buildUpName:str):
    return [
        BuildUp(
            id=1, 
            name=buildUpName,
            type="AW 1.1",
            layers=[Layer(id=1, name="Layer 1")]
            )
        ]
# =========================================================================================
#  Query
# =========================================================================================
@strawberry.type
class Query:
    @strawberry.field
    def build_ups(self, buildUpName:str) -> List[BuildUp]:
        return get_build_ups(buildUpName=buildUpName)
    requirement_profiles: List[RequirementProfile]
# =========================================================================================
#  Mutation
# =========================================================================================
@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_build_up(self, name: str, description: Optional[str] = None) -> BuildUp:
        return BuildUp(name=name, description=description)
    @strawberry.mutation
    def add_requirement_profile(self, name: str, description: Optional[str] = None) -> RequirementProfile:
        return RequirementProfile(name=name, description=description)
    @strawberry.mutation
    def add_layer(self, buildUpName: str, name: str, description: Optional[str] = None) -> Layer:
        buildUp = get_build_ups(buildUpName=buildUpName)
        buildUp.layers.append(Layer(name=name, description=description))
        return Layer(buildUpName=buildUpName, name=name, description=description)
    