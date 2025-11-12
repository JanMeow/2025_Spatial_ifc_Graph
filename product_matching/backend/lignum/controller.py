from fastapi import FastAPI, HTTPException, APIRouter
from lignum.model import LignumResponse, lignum_references
import requests
# =========================================================================================
#  Lignum Router
# =========================================================================================
router = APIRouter(tags = ["lignum"])

@router.get("/{product_name}", response_model=LignumResponse)
async def get_lignum_data(product_name: str):  
    """Get Lignum data for a specific wall type"""
    if product_name not in lignum_references:
        raise HTTPException(status_code=404, detail=f"Wall '{product_name}' not found in Lignum references")
    laufnummer = lignum_references[product_name]
    try:
        url = f"https://lignumdata.ch/api/v1.cfc?method=getBauteil&condition={{\"laufnummer\": \"{laufnummer}\"}}"
        response = requests.get(url)        
        data = response.json()
        if not data:
            raise HTTPException(status_code=404, detail=f"No Lignum data found for {laufnummer}")
        # Extract the first (and should be only) result
        lignum_data = data[0]
        # Extract height and weight from messwertsatz if available
        messwertsatz = lignum_data.get('messwertsatz', {})
        # Extract GWP from oekobilanz if available
        oekobilanz = lignum_data.get('oekobilanz', {})
        
        return LignumResponse(
            bauteilname=lignum_data.get('bauteilname', ''),
            katalognr=lignum_data.get('katalognr', ''),
            laufnummer=lignum_data.get('laufnummer', ''),
            uwert=lignum_data.get('uwert', ''),
            aufbauhoehe=messwertsatz.get('hoehe'),
            gewicht=messwertsatz.get('gewicht'),
            gwp=oekobilanz.get('gwp'),
            media=lignum_data.get('media', {}),
            bauteiltyp=lignum_data.get('bauteiltyp', {}),
            fassadentyp=lignum_data.get('fassadentyp', {}),
            bekleidung=lignum_data.get('bekleidung', {}),
            daemmwerte=lignum_data.get('daemmwerte', {}),
            quellekonstruktion=lignum_data.get('quellekonstruktion', {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Lignum data: {str(e)}")