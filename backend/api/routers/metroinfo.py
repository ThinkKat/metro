from fastapi import Depends, APIRouter

from api.dependencies.dependencies import get_metro_repository, get_timetable_repository
from model.pydantic_model import StationSearchbarList, StationInfo, Timetable, TimetableRow
from utils.utils import op_date

router = APIRouter()

@router.get("/search/stations", tags = ["metroinfo"])
async def get_stations(repo = Depends(get_metro_repository)) -> list[StationSearchbarList]:
    data = repo.find_stations_searchbar()
    return data

@router.get("/information/{station_public_code}", tags = ["metroinfo"])
async def get_station_info(station_public_code: str,
                           metro_repo = Depends(get_metro_repository), 
                           tb_repo = Depends(get_timetable_repository)) -> StationInfo:
    data = metro_repo.find_total_station_info(station_public_code)
    data.timetables = tb_repo.find_timetable_by_station_public_code(op_date(), station_public_code)
    return data



