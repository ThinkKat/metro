from fastapi import APIRouter

from ..data_model.data_model import StationSearchbarList, StationInfo

router = APIRouter()

@router.get("/search/stations", tags = ["metroinfo"])
async def get_stations() -> list[StationSearchbarList]:
    return 

@router.get("/information/{station_public_code}", tags = ["metroinfo"])
async def get_station_info(station_public_code: str) -> StationInfo:
    return 
