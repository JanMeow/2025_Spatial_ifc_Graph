from pydantic import BaseModel, Field
from typing import Literal, Optional
class Sampling(BaseModel):
    sampling_method: Optional[Literal["horizontal", "vertical"]] = "horizontal"