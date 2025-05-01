from fastapi import APIRouter

from model.pydantic_model import RealtimeData

router = APIRouter()

@router.get("/realtimes/{station_public_code}", tags = ["realtimes"])
async def get_realtime_info(station_public_code: str) -> RealtimeData:
    return 
