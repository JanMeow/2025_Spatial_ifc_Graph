from pydantic import BaseModel
from typing import List, Dict
import numpy as np
from buildups.service import load_data_from_excel
# =========================================================================================
#  BuildUp Model
# =========================================================================================
class BuildUps(BaseModel):
    """Repository for build ups"""
    data_file_path: str = "data/data_SH.xlsx"
    data: dict = load_data_from_excel(data_file_path)

buildups = BuildUps()