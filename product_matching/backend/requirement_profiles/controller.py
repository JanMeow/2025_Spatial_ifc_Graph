from fastapi import APIRouter, HTTPException
from fastapi.exceptions import RequestValidationError
from requirement_profiles.model import RequirementProfileResponse, RequirementProfileRequest
from buildups.model import buildups
from requirement_profiles.service import filter_all_buildups
from cache.service import CacheDep, cleanup_cache

import json
# =========================================================================================
router = APIRouter( tags = ["requirement_profiles"])
# =========================================================================================
#  Requirement Profiles Router
# =========================================================================================
@router.get("/{profile_id}")
async def get_requirement_profile(profile_id: str):
    """Get a requirement profile by ID"""
    return {"profile_id": profile_id}

@router.post("/apply", response_model=RequirementProfileResponse)
async def filter_requirement_profiles(request: RequirementProfileRequest, cache: CacheDep):
    """Filter data based on parameters with dynamic sampling"""
    #Will be fetched from DB in the future
    buildups_data = buildups.data    
    if request.product not in buildups_data and "All" not in request.product:   
        raise HTTPException(status_code=404, detail=f"Wall '{request.product}' not found")
    results = filter_all_buildups(request, buildups_data, cache)
        
    cleanup_cache(cache)
    return results