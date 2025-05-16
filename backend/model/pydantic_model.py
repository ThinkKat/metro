from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field

class Line(BaseModel):
    line_id: int
    line_color: str
    line_name: str
    
class TransferLine(Line):
    station_public_code: str

class Station(BaseModel):
    station_public_code: str
    station_id: int # If station_id is 0, there are no realtime information
    station_name: str
    request_station_name: Optional[str]
    left_direction: int
    right_direction: int
    up: str
    down: str

class AdjacentStation(Station):
    up_down: int  # 0 = 상행, 1 = 하행
    
# The data model of instance of searchbar list 
# TODO: Create StationSearchbar model.
# TODO: Change this model to List type of "StationSearchbar"
class StationSearchbarList(BaseModel):
    line_id: int
    line_color: str
    line_name: str
    station_public_code: str
    station_name: str

# The data model of an instance of realtime position 
class RealtimePositionRow(BaseModel):
    line_id: int
    train_id: str
    station_id: int
    station_name: str
    last_station_id: int
    last_station_name: str
    received_at: str
    train_status: int
    express: int
    up_down: int

"""
    The data model of an instance of realtime information
    The sources of realtime data are different by the metro line.
    
    1077(신분당선): Arrival information API, realtimeStationArrival/ALL
        Arrival information is used almost without preprocessing. Just parsing the information message attributes.
        
    The rest of metro lines: Place information API, realtimePosition/{line_name}
        Place information is used with preprocessing using the timetable data.
"""
class RealtimeArrivalRow(BaseModel):
    train_id: str
    first_station_name: Optional[str] = None
    last_station_name: str
    searched_station_name: Optional[str] = None
    cur_station_name: str 
    received_at: datetime # YYYY-MM-DD HH:MM:SS
    train_status: str
    express: int
    express_non_stop: Optional[int] = None
    up_down: int
    current_delayed_time: Optional[float] = None
    expected_delayed_time: Optional[float] = None # This attribute is used after it is possible to calculate expected delayed time.
    expected_left_time: Optional[int] = None # unit: second
    expected_arrival_time: Optional[str] = None 
    stop_order_diff: Optional[int] = None # 남은 정차역 수
    information_message: Optional[str] = None
    searched_station_department_time: Optional[time] = None # of searched station 
    searched_station_arrival_time: Optional[time] = None # of searched station

# The data model of realtime position info
class RealtimePosition(BaseModel):
    place: List[RealtimePositionRow]
    
# The data model of realtime station info
# This model is divided into left and right.
class RealtimeArrival(BaseModel):
    left: List[RealtimeArrivalRow]
    right: List[RealtimeArrivalRow]

# The data model of realtime data
# The line attribute is realtime position data
# The station attribute is realtime arrival data
class RealtimeData(BaseModel):
    line: Optional[RealtimePosition] = None
    station: Optional[RealtimeArrival] = None

# The data model of instance of timetable data
class TimetableRow(BaseModel):
    train_id: str
    first_station_name: str
    last_station_name: str
    arrival_time: Optional[time]  # "HH:mm:ss"
    department_time: Optional[time]  # "HH:mm:ss"
    up_down: int
    express: int  # 0 = 일반, 1 = 급행
    sort_hour_key: int
    sort_minute_key: int
    mean_delayed_time: Optional[float] = None
    cnt_over_300s_delay: Optional[int] = None

# The data model of timetable info of a station
# This model is divided into left and right.
class Timetable(BaseModel):
    left: List[TimetableRow]
    right: List[TimetableRow]

# The data model of Station information
# TODO: the name of attribute "realtime_station" have to be substituted to "realtime_arrival"
class StationInfo(BaseModel):
    line: Line
    station: Station
    adjacent_stations: dict[str, List[AdjacentStation]]
    transfer_lines: List[TransferLine]
    has_realtimes: bool = False
    has_timetables: bool = False
    realtime_station: Optional[RealtimeArrival] = None
    realtime_line: Optional[RealtimePosition] = None
    timetables: Optional[dict[str, Timetable]] = Field(default_factory=dict)