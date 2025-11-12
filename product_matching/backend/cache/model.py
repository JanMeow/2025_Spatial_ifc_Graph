from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
import numpy as np
class Cache(BaseModel):
    max_cahce_size: int = 40
    results: Dict[str, Any] = Field(default_factory=dict)

