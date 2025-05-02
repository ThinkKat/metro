from fastapi import Depends, APIRouter

from api.dependencies.tmp_data_client import get_position_by_line_id, get_arrival_by_station_id
from api.dependencies.dependencies import get_metro_repository
from model.pydantic_model import RealtimeData

router = APIRouter()

@router.get("/information/realtimes/{station_public_code}", tags = ["realtimes"])
async def get_realtime_info(station_public_code: str, repo = Depends(get_metro_repository)) -> RealtimeData:
    station = repo.find_station(station_public_code)
    realtime_position = get_position_by_line_id(station["line_id"])
    realtime_arrival = get_arrival_by_station_id(station["station_id"], station["up"], station["down"])
    return RealtimeData(**{
        "line": realtime_position,
        "station": realtime_arrival
    })

