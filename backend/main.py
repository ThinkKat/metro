import os
import logging

from fastapi import FastAPI

from packages.db_manager import DBManager
from packages.timetable_db_manager import TimetableDBManager
from packages.get_subway_information import get_subway_data
from packages.get_realtime_information import get_realtime_line_data, get_realtime_station_data
from packages.data_model import StationSearchbar, Station, RealtimeLine, SubwayData, RealtimeData

logger1 = logging.getLogger("uvicorn.error")
logger2 = logging.getLogger("uvicorn.access")

fh = logging.FileHandler('./log/fastapi.log', mode='a')
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to fh
fh.setFormatter(formatter)

logger1.addHandler(fh)
logger2.addHandler(fh)

app = FastAPI()
timetable_db_manager = TimetableDBManager()

@app.get("/api/metro")
async def subways() -> dict:  
    return {"description": "This is the API for subway data"}

@app.get("/api/metro/search/stations")
async def get_station_information() -> list[StationSearchbar]:
    return timetable_db_manager.get_stations_searchbar()

@app.get("/api/metro/information/{station_public_code}")
async def get_subway_data_by_public_code(station_public_code: str) -> SubwayData|dict:
    subway_data = get_subway_data(station_public_code)
    
    # If subway_data has error message
    if "error" in subway_data:
        return subway_data
        
    return subway_data

@app.get("/api/metro/information/realtimes/{station_public_code}")
async def get_realtimes_data_by_public_code(station_public_code: str) -> RealtimeData|dict:
    station_info = timetable_db_manager.get_station_info(station_public_code)
    
    # If station_info has error message
    if "error" in station_info:
        return station_info 
    
    # If station_info has no realtime information
    if station_info["station_id"] == 0:
        return {
            "error": "There exists no realtime information.",
            "station_public_code": station_public_code
        }
    
    line_info = timetable_db_manager.get_line_info(station_info["line_id"])
    station = Station(**station_info)
    realtime_line_data = get_realtime_line_data(line_info["line_name"])
    realtime_station_data = get_realtime_station_data(
        station_info["line_id"],
        station.request_station_name,
        {
            0: station.up,
            1: station.down
        }
    )
    
    realtime_data = RealtimeData()
    
    if 'error' not in realtime_line_data:
        realtime_data.line = realtime_line_data
    if 'error' not in realtime_station_data:
        realtime_data.station = realtime_station_data
    return realtime_data


@app.get("/api/metro/information/realtimes/line/{line_id}")
async def get_realtimes_data_by_public_code(line_id: int) -> RealtimeLine|dict:
    line_info = timetable_db_manager.get_line_info(line_id)
    realtime_line_data = get_realtime_line_data(line_info["line_name"])
    return realtime_line_data

if __name__ == "__main__":
    pass