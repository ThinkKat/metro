import os

from fastapi import FastAPI

from packages.metro_info_manager import MetroInfoManager
from packages.get_metro_information import get_metro_data
from packages.process_worker import ProcessWorker
from packages.data_model import StationSearchbarList, Station, StationInfo, RealtimeData
from packages.utils import op_date, check_holiday

# Check whether log file directory exists
if not os.path.exists('log'):
    os.mkdir('log')

app = FastAPI()

# Station information from sqlite db
metro_info_manager = MetroInfoManager()

# Caching realtime data of all stations intervally
pw = ProcessWorker()
pw.start()

@app.get("/api/metro")
async def subways() -> dict:  
    return {
        "description": "This is the API for metro data",
        "check_thread_alive": pw.check_is_alive()}

@app.get("/api/metro/search/stations")
async def get_station_information() -> list[StationSearchbarList]:
    return metro_info_manager.get_stations_searchbar()

@app.get("/api/metro/information/{station_public_code}")
async def get_subway_data_by_public_code(station_public_code: str) -> StationInfo|dict:
    
    subway_data = get_metro_data(op_date(), station_public_code)
    # If subway_data has error message
    if "error" in subway_data:
        return subway_data
    return subway_data

@app.get("/api/metro/information/realtimes/{station_public_code}")
async def get_realtimes_data_by_public_code(station_public_code: str) -> RealtimeData|dict:
    station_info = metro_info_manager.get_station_info(station_public_code)
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
    line_info = metro_info_manager.get_line_info(station_info["line_id"])
    
    if line_info["line_id"] not in pw.realtime_process.realtime_position:
        realtime_line_data = {
            "error": "There exists no realtime position information.",
            "line_id": line_info["line_id"]
        }
    else:
        realtime_line_data = pw.realtime_process.realtime_position[line_info["line_id"]]
    
    # Realtime Arrival of Stations
    if station.station_id not in pw.realtime_process.arrival_hashmap:
        # Case that there exists no realtime data
        realtime_station_arrival = {
            "error": "There exists no realtime station information.",
            "station_public_code": station_public_code
        }
    else:
        # Get data from interval process 
        realtime_station_arrival = pw.realtime_process.get_data_by_station_id(station.station_id, station.up, station.down)
    
    realtime_data = RealtimeData()
    if 'error' not in realtime_line_data:
        realtime_data.line = realtime_line_data
    if 'error' not in realtime_station_arrival:
        realtime_data.station = realtime_station_arrival
    return realtime_data

if __name__ == "__main__":
    pass