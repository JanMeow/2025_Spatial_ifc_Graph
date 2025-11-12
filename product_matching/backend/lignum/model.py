from pydantic import BaseModel
from typing import Optional
# =========================================================================================
#  Schema: Lignum Response
# =========================================================================================
class LignumResponse(BaseModel):
    bauteilname: Optional[str] = None
    katalognr: Optional[str] = None
    laufnummer: Optional[str] = None
    uwert: Optional[str] = None
    aufbauhoehe: Optional[float] = None
    gewicht: Optional[float] = None
    gwp: Optional[float] = None
    media: Optional[dict] = None
    bauteiltyp: Optional[dict] = None
    fassadentyp: Optional[dict] = None
    bekleidung: Optional[dict] = None
    daemmwerte: Optional[dict] = None
    quellekonstruktion: Optional[dict] = None
# =========================================================================================
#  Domain: Lignum References
# =========================================================================================
lignum_references = {
    "Aussenwand 1.1": "D0100",
    "Aussenwand 1.2": "D0085",
    "Aussenwand 1.3": "D0260",
    "Aussenwand 1.7": "D0083",
    "Aussenwand 1.8": "D0258",
}