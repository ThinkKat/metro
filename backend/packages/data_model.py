from pydantic import BaseModel, Field
from typing import List, Optional

class Line(BaseModel):
    line_id: int
    line_color: str
    line_name: str
    
class StationSearchbar(BaseModel):
    line_id: int
    line_color: str
    line_name: str
    station_public_code: str
    station_name: str

class Station(BaseModel):
    station_public_code: str
    station_id: int # If station_id is 0, there are no realtime information
    station_name: str
    request_station_name: str|None
    left: int
    right: int
    up: str
    down: str

class AdjacentStation(Station):
    up_down: int  # 0 = 상행, 1 = 하행

class TransferLine(Line):
    station_public_code: str
    
class RealtimeRow(BaseModel):
    train_id: str
    first_station_name: str|None = None
    last_station_name: str
    searched_station_name: str | None = None
    cur_station_name: str 
    received_at: str # YYYY-MM-DD HH:MM:SS
    train_status: str
    express: int
    express_non_stop: int|None = None
    up_down: int
    current_delayed_time: float|None = None
    expected_delayed_time: float|None = None
    expected_left_time: int|None = None # unit: second
    expected_arrival_time: str|None = None 
    stop_order_diff: int|None = None # 남은 정차역 수
    information_message: str|None = None
    searched_station_department_time: str|None = None # of searched station 
    searched_station_arrival_time: str|None = None # of searched station

class RealtimeLine(BaseModel):
    place: List[RealtimeRow]
    
class RealtimeStation(BaseModel):
    left: List[RealtimeRow]
    right: List[RealtimeRow]
    
class RealtimeData(BaseModel):
    line: Optional[RealtimeLine] = None
    station: Optional[RealtimeStation] = None

class TimetableRow(BaseModel):
    train_id: str
    first_station_name: str
    last_station_name: str
    arrival_time: str | None  # "HH:mm:ss"
    department_time: str | None  # "HH:mm:ss"
    up_down: int
    express: int  # 0 = 일반, 1 = 급행
    sort_hour_key: int
    sort_minute_key: int

class Timetable(BaseModel):
    left: List[TimetableRow]
    right: List[TimetableRow]

class SubwayData(BaseModel):
    line: Line
    station: Station
    adjacent_stations: dict[str, List[AdjacentStation]]
    transfer_lines: List[TransferLine]
    has_realtimes: bool = False
    has_timetables: bool = False
    realtime_station: Optional[RealtimeStation] = None
    realtime_line: Optional[RealtimeLine] = None
    timetables: Optional[dict[str, Timetable]] = Field(default_factory=dict)