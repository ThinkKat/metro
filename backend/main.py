from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from packages.db_manager import DBManager
from packages.timetable_db_manager import TimetableDBManager
from packages.get_subway_information import get_subway_data
from packages.get_realtime_information import get_realtime_line_data, get_realtime_station_data
from packages.data_model import StationSearchbar, Station, RealtimeLine, SubwayData, RealtimeData

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React 앱의 URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

timetable_db_manager = TimetableDBManager()

@app.get("/")
async def home() -> dict:    
    return {"description": "This is the API for subway data"}

@app.get("/subways/search/stations")
async def get_station_information() -> list[StationSearchbar]:
    return timetable_db_manager.get_stations_searchbar()

@app.get("/subways/information/{station_public_code}")
async def get_subway_data_by_public_code(station_public_code: str) -> SubwayData|dict:
    subway_data = get_subway_data(station_public_code)
    
    # If subway_data has error message
    if "error" in subway_data:
        return subway_data
    
    # If subway_data has realtime information 
    if subway_data.has_realtimes:
        realtime_line_data = get_realtime_line_data(subway_data.line.line_name)
        realtime_station_data = get_realtime_station_data(
            subway_data.line.line_id, 
            subway_data.station.request_station_name,
            {
                0: subway_data.station.up,
                1: subway_data.station.down
            }
        )
        if 'error' not in realtime_line_data:
            subway_data.realtime_line = realtime_line_data
        if 'error' not in realtime_station_data:
            subway_data.realtime_station = realtime_station_data
        
    return subway_data

@app.get("/subways/information/realtimes/{station_public_code}")
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
    return RealtimeData(line = realtime_line_data, station = realtime_station_data)


@app.get("/subways/information/realtimes/line/{line_id}")
async def get_realtimes_data_by_public_code(line_id: int) -> RealtimeLine|dict:
    line_info = timetable_db_manager.get_line_info(line_id)
    realtime_line_data = get_realtime_line_data(line_info["line_name"])
    return realtime_line_data
