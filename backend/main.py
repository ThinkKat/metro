from fastapi import FastAPI

from packages.config import INTERVAL
from packages.timetable_db_manager import TimetableDBManager
from packages.get_subway_information import get_subway_data
from packages.realtime_arrival import IntervalThread
from packages.get_realtime_information import RealtimeInformation
from packages.data_model import StationSearchbar, Station, SubwayData, RealtimeData
from packages.utils import op_date, check_holiday

app = FastAPI()

# Station information from sqlite db
timetable_db_manager = TimetableDBManager()
realtime_information = RealtimeInformation()

# Caching realtime data of all stations intervally
it = IntervalThread(INTERVAL)
it.start()

@app.get("/api/metro")
async def subways() -> dict:  
    return {
        "description": "This is the API for metro data", 
        "interval_thread_alive": it.checkIsAlive()
    }

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
    station = Station(**station_info)
    # If station_info has no realtime information
    if station_info["station_id"] == 0:
        return {
            "error": "There exists no realtime information.",
            "station_public_code": station_public_code
        }
        
    # Realtime Postion of Lines
    line_info = timetable_db_manager.get_line_info(station_info["line_id"])
    data = realtime_information.get_realtime_data("realtimePosition", line_info["line_name"])
    realtime_line_data = realtime_information.postprocess_realtime_position(data)
    
    # Realtime Arrival of Stations
    if station.station_id not in it.realtime_arrival.arrival_hashmap:
        # Case that there exists no realtime data
        realtime_station_arrival = {
            "error": "There exists no realtime station information.",
            "station_public_code": station_public_code
        }
    else:
        # Get data from interval process 
        realtime_station_arrival = it.realtime_arrival.get_data_by_station_id(station.station_id, station.up, station.down)
    
    realtime_data = RealtimeData()
    if 'error' not in realtime_line_data:
        realtime_data.line = realtime_line_data
    if 'error' not in realtime_station_arrival:
        realtime_data.station = realtime_station_arrival
    return realtime_data

if __name__ == "__main__":
    pass