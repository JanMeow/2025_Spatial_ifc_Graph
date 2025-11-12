from fastapi import FastAPI, HTTPException, APIRouter, Depends
from typing import List
from buildups.model import buildups
from auth.service import get_access_token
import requests
# ====================================
#Products (main resource)
# ====================================
router = APIRouter(tags=["buildups"])
@router.get("/", response_model=List[str])
def get_buildups():
    """Get list of available product types"""
    return list(buildups.data.keys())
@router.get("/{buildup_type}", response_model=List[str])
def get_buildups_by_type(buildup_type: str):
    """Get list of available product types e.g Aussenwand, Innenwand, Decke"""
    return ["All"] + [k for k in buildups.data.keys() if buildup_type in k]
@router.get("/{buildup_type}/{buildup_name}")
def get_buildups(buildup_type: str, buildup_name: str):
    """Get a specific product"""
    if buildup_name not in buildups.data:
        raise HTTPException(status_code=404, detail=f"Product '{buildup_name}' not found")
    return buildups.data[buildup_name]
@router.get("/{buildup_type}/{buildup_name}/layers")
def get_buildups_layers(buildup_type: str, buildup_name: str):
    """Get layers for a specific product"""
    if buildup_name not in buildups.data:
        raise HTTPException(status_code=404, detail=f"Product '{buildup_name}' not found")
    buildup_data = buildups.data[buildup_name]
    layers = buildup_data["variants"]
    # Convert numpy arrays to lists for JSON serialization
    layers_dict = {layer_name: layer_data.tolist() 
    if hasattr(layer_data, "tolist") else layer_data for layer_name, layer_data in layers.items()}
    return {"product_name": buildup_name, "layers": layers_dict}
@router.get("/dokwood_platform/{tenant_slug}")
def get_build_ups_from_dokwood_platform(tenant_slug: str, access_token: str = Depends(get_access_token)):
    """Get build ups from Dokwood platform"""
    platform_api ="https://sex8vpnxfz.eu-central-1.awsapprunner.com/graphql"
    query = """
    query StandardBuildupsOp($input: GetStandardBuildupsInputDto!) {
    standardBuildups(input: $input) {buildups {buildup {_id properties {value {dataType unit value}}}}}}
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-tenant-slug": tenant_slug
    }
    payload = {
        "query": query,
        "variables": {"input": {"tenantSlug":tenant_slug,"isReleased": True}},
        "operationName": "StandardBuildupsOp"
    }

    try:
        response = requests.post(platform_api,json =payload, headers=headers)
        build_ups = response.json()["data"]["standardBuildups"]["buildups"]
    except Exception as e:
        raise Exception(f"Error logging in: {e}")
    return build_ups
