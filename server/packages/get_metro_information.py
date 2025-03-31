import sys
import time
from operator import attrgetter

from .metro_info_manager import MetroInfoManager
from .data_model import Line, Station, AdjacentStation, TransferLine, TimetableRow, Timetable, SubwayData

metro_info_manager = MetroInfoManager()

def get_metro_data(op_date: str, station_public_code: str) -> SubwayData|dict:
    
    # Station Info
    station_info = metro_info_manager.get_station_info(station_public_code)
    
    if "error" in station_info:
        # Return error message
        return station_info
    station = Station(**station_info)
    
    # Line Info
    line_id = station_info["line_id"]
    line_info = metro_info_manager.get_line_info(line_id)
    line = Line(**line_info)
    
    # Convert up_down to direction
    adj_stations = {"left": [],"right": []}
    connections = metro_info_manager.get_adjacent_stations(station_public_code)
    
    for c in connections: 
        station_info = metro_info_manager.get_station_info(c["to_station_public_code"])
        adj_station = AdjacentStation(**station_info, up_down = c["up_down"])
        adj_stations[c["direction"]].append(adj_station)

    transfer_info = metro_info_manager.get_transfer_lines(line_id, station_public_code)
    # Add current line
    transfer_lines = [TransferLine(**line_info, station_public_code = station.station_public_code)]

    for ts in transfer_info: 
        line_info = metro_info_manager.get_line_info(ts["line_id"])
        transfer_line = TransferLine(**line_info, station_public_code = ts["station_public_code"])
        transfer_lines.append(transfer_line)
    transfer_lines = sorted(transfer_lines, key = lambda x : x.line_id)
        
    timetable_info = metro_info_manager.get_timetable(op_date, station_public_code)
    
    timetable = {
        "weekday": {
            "left": [],
            "right": []
        },
        "holiday": {
            "left": [],
            "right": []
        }
    }
    
    for t in timetable_info:
        direction = "up" if t["up_down"] == 0 else "down"
        t["sort_hour_key"] = t["department_time"].hour if t["department_time"] is not None else 99
        t["sort_hour_key"] = t["sort_hour_key"] + 24 if t["sort_hour_key"] < 5 else t["sort_hour_key"]
        t["sort_minute_key"] = t["department_time"].minute if t["department_time"] is not None else 99
        
        if t["day_code"] == 8:
            timetable["weekday"][station.__getattribute__(direction).split("_")[0]].append(TimetableRow(**t))
        else:
            timetable["holiday"][station.__getattribute__(direction).split("_")[0]].append(TimetableRow(**t))
    
    timetables = {k:Timetable(**v) for k, v in timetable.items()} 
    has_timetables = len(timetable_info) != 0
    
    timetables["weekday"].left = sorted(timetables["weekday"].left, key=attrgetter("sort_hour_key", "sort_minute_key"))
    timetables["weekday"].right = sorted(timetables["weekday"].right, key=attrgetter("sort_hour_key", "sort_minute_key"))
    timetables["holiday"].left = sorted(timetables["holiday"].left, key=attrgetter("sort_hour_key", "sort_minute_key"))
    timetables["holiday"].right = sorted(timetables["holiday"].right, key=attrgetter("sort_hour_key", "sort_minute_key"))
      
    subway_data = SubwayData(
        line= line,
        station=station,
        adjacent_stations=adj_stations,
        transfer_lines=transfer_lines,
        has_realtimes=station.station_id != 0,
        has_timetables=has_timetables,
        realtimes={},
        timetables=timetables
    )
    return subway_data
    
if __name__ == "__main__":
    argument = sys.argv
    op_date = argument[1]
    station_public_code = argument[2]
    
    start = time.time()
    subway_data = get_metro_data(op_date, station_public_code)
    
    print(subway_data.station)
    print(f"{time.time()-start:.5f}")