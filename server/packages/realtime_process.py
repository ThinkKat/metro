import logging
import traceback
import time
from datetime import datetime, timedelta
from multiprocessing.connection import Client

import pandas as pd

from .utils import op_date, check_holiday, is_next_date
from .timetable_db_manager import TimetableDBManager
from .data_model import RealtimeRow, RealtimePositionRow, RealtimePosition, RealtimeStation

logger = logging.getLogger("realtime-process")
address = ('localhost', 6000)

class RealtimeProcess:
    def __init__(self, address = address):
        self.address = address
        
        # To convert train status code 
        self.train_status = {
            0: "진입", 1: "도착", 2: "출발", 3: "전역출발", 4: "전역진입", 5: "전역도착", 99: "운행중"}
        
        # Connect to socket pipe
        self.connect()
        
        # Set data, op_date, timetable data
        self.init()
        
    def init(self):
        # timetable information
        self.timetable_db_manager = TimetableDBManager()
        
        # Realtime data from interval collection worker
        self.init_data()
        # Set operational date
        self.set_op_date()
        # Load static data: timetable data
        self.set_timetable_data()
        
        logger.info("Initialize realtime data, operational date, and timetable data")
    
    def connect(self):
        # Client
        try:
            self.client = Client(self.address)
            logger.info("Connected to listener")
        except ConnectionRefusedError:
            # This excpetion is raised when the pipe isn't opening.
            logger.error(traceback.format_exc())
            time.sleep(5)
            self.client = None
        except Exception:
            logger.error(traceback.format_exc())
            self.client = None
    
    def init_data(self):
        # Realtime Positon data
        self.realtime_position: dict[int, RealtimePosition] = {}
        # Realtime Arrival data
        self.arrival_hashmap: dict[int, list[RealtimeRow]] = {}
    
    def set_op_date(self):
        # Set operation date
        # op_date criteria: 04:50 - tomorrow 04:50
        self.op_d = op_date(datetime_ = datetime.now())
        self.next_d = self.op_d + timedelta(days=1)
        # Formatting
        self.op_d_str = self.op_d.strftime("%Y-%m-%d")
        self.next_d_str = self.next_d.strftime("%Y-%m-%d")
        self.day_code = 9 if check_holiday(self.op_d) else 8
        logger.info(f"{self.op_d}: {"Weekday" if self.day_code == 8 else "Holiday"}")
        
    def set_timetable_data(self):
        self.tb: pd.DataFrame = self._load_timetable_data() 
    
    def _load_timetable_data(self) -> pd.DataFrame:
        # load timetable data
        # using self attributes
        data = self.timetable_db_manager.execute("""
                SELECT 
                    tb.*,
                    s.station_id,
                    s.station_name
                FROM final_timetable tb
                INNER JOIN stations s
                ON tb.line_id = s.line_id
                AND tb.station_public_code = s.station_public_code
                AND tb.day_code = :day_code
            """,
            {"day_code": self.day_code}
        )
        columns = self.timetable_db_manager.get_column_names()
        tb = pd.DataFrame(data, columns=columns).drop(columns = "train_id") # Using instead of realtime_train_id column
        
        # Convert time to datetime
        tb["arrival_datetime"] = tb["arrival_time"]
        tb.loc[~tb["arrival_time"].isna(), "arrival_datetime"] = tb.loc[~tb["arrival_time"].isna(),"arrival_time"].apply(lambda x : self.next_d_str + " " + x if is_next_date(x) else self.op_d_str + " " + x)
        tb["department_datetime"] = tb["department_time"]
        tb.loc[~tb["department_time"].isna(), "department_datetime"] = tb.loc[~tb["department_time"].isna(), "department_time"].apply(lambda x : self.next_d_str + " " + x if is_next_date(x) else self.op_d_str + " " + x)
        
        return tb
    
    def _process_arrival_all_data(self, data: list[dict]) -> dict[int, list]:
        # New data hashmap
        data_hashmap: dict[int, list] = {}
        for row in data:
            # Filtering necessary data
            if int(row["subwayId"]) not in [1032, 1077, 1094]: continue
            
            station_id = int(row["statnId"])
            # Extract necessary attributes
            new_row = {
                "train_id": row["btrainNo"],
                "last_station_name": row["bstatnNm"],
                "searched_station_name": row["statnNm"],
                "cur_station_name": row["arvlMsg3"],
                "received_at": row["recptnDt"],
                "express": 1 if row["btrainSttus"] == "급행" else 0,
                "train_status": self.train_status[int(row["arvlCd"])],
                "up_down": 0 if row["updnLine"] == "상행" else 1,
                "expected_left_time": int(row["barvlDt"]),
                "information_message": row["arvlMsg2"]
            }
            
            if station_id not in data_hashmap:
                data_hashmap[station_id] = [new_row]
            else:
                data_hashmap[station_id].append(new_row)
        return data_hashmap
    
    def _calculate_arrival_data(self, realtime_position: pd.DataFrame) -> pd.DataFrame:
        # Data join
        data_join = pd.merge(
            realtime_position[["line_id", "station_id", "train_id", "received_at", "train_status"]],
            self.tb,
            left_on = ["line_id", "train_id", "station_id"],
            right_on = ["line_id", "realtime_train_id", "station_id"],
            how = "inner" # 정보 파싱 가능한 데이터만
        )
        # Modify date value
        data_join["received_at"] = data_join["received_at"].str.split(" ", expand=True)[1].apply(lambda x : self.next_d_str + " " + x if is_next_date(x) else self.op_d_str + " " + x)

        # Calculate delayed time
        # Datetime foramt is %Y-%m-%d %H:%M:%S or %Y-%m-%d %H:%M
        datetime_format = "ISO8601"
        
        data_join["received_at_dt"] = pd.to_datetime(data_join["received_at"].str.strip(), format=datetime_format)
        data_join["arrival_datetime_dt"] = pd.to_datetime(data_join["arrival_datetime"].str.strip(), format=datetime_format)
        data_join["department_datetime_dt"] = pd.to_datetime(data_join["department_datetime"].str.strip(), format=datetime_format) 
        
        data_join.loc[data_join["train_status"]<=1, "delayed_time"] = data_join["received_at_dt"] - data_join["arrival_datetime_dt"]
        data_join.loc[data_join["train_status"]==2, "delayed_time"] = data_join["received_at_dt"] - data_join["department_datetime_dt"]
        
        """
            Adjust to delayed_time of coming train time.
            Trains status == 0 -> 접근
            
            Coming train is about 30 seconds before arrival. 
            delayed_time when train_status is coming
                received_at - (arrival_datetime - 30s) 
                = received_at - arrival_datetime + 30s
                = delayed_time of arrival + 30s
        """
        data_join.loc[data_join["train_status"]==0, "delayed_time"] += pd.to_timedelta(30, unit = 's') 
        
        
        # Join next timetable data
        # Next suffix means searched station.
        arrival = pd.merge(
            data_join,
            self.tb,
            left_on = ["line_id", "train_id"],
            right_on = ["line_id", "realtime_train_id"],
            how = "inner",
            suffixes=("","_next")
        )

        """
            Masking valid data
            1. Stations that isn't yet passed (stop_no <= stop_no_next)
            2. Stations where the express train isn't stopped. (express_non_stop_next == 0)
        """
        mask = (arrival["stop_no"] <= arrival["stop_no_next"]) & (arrival["express_non_stop_next"] == 0)
        arrival = arrival[mask].reset_index(drop = True)
        
        """
            Calculate arrival information
            1. "diff" is the difference between a current station order and a searched station order
            2. "expected_arrival_time"  = searched_arrival_datetime + expected_delayed_time
                Currently, expectd_delayed_time can't be able to calculate "expected_delayed_time"
                So, use delayed_time instead of this attribute. Delayed time means a delayed time in current train status.
        """
        arrival["diff"] = arrival["stop_no_next"] - arrival["stop_no"]
        arrival["expected_arrival_time"] = pd.to_datetime(arrival["arrival_datetime_next"]) + arrival['delayed_time']
        arrival["expected_arrival_time"] = arrival["expected_arrival_time"].astype("string")
        
        """
            Convert delayed_time to seconds unit.
            Before converting, dtype of delayed_time is timedelta[64].
        """
        arrival["delayed_time"] = (arrival["delayed_time"].dt.total_seconds()).round(decimals=0)
        
        # Change column names
        change_cols = {
            "diff": "stop_order_diff",
            "delayed_time": "current_delayed_time",
            "station_name": "cur_station_name",
            "station_id_next": "searched_station_id",
            "station_name_next": "searched_station_name",
            "arrival_time_next": "searched_station_arrival_time" ,
            "department_time_next": "searched_station_department_time",
            "express_non_stop_next": "searched_express_non_stop"
        }
        
        # Sort values bt stop_order_diff
        arrival = arrival.rename(columns=change_cols).sort_values("stop_order_diff")
        
        return arrival
    
    def process_realtime_data(self, position_data: pd.DataFrame|None, arrival_data: list[dict]|None):
        # 1032, 1077, 1094 data
        
        if position_data is not None:
            arrival: pd.DataFrame = self._calculate_arrival_data(position_data)
            # Realtime Position Data
            realtime_position_by_line_id = {}
            for d in position_data.to_dict(orient="records"):
                line_id = d["line_id"]
                if line_id not in realtime_position_by_line_id:
                    realtime_position_by_line_id[line_id] = [d]
                else:
                    realtime_position_by_line_id[line_id].append(d)
            self.realtime_position = {
                k:RealtimePosition(place = [RealtimePositionRow(**v) for v in values]) for k, values in realtime_position_by_line_id.items()
            }
        
        if arrival_data is not None:
            arrival_hashmap: dict[int, list] = self._process_arrival_all_data(arrival_data)
            # Add arrival data
            for d in arrival.to_dict(orient="records"):
                if not d["line_id"] in [1032, 1077, 1094]:
                    station_id = d["searched_station_id"]
                    d["train_status"] = self.train_status[d["train_status"]]
                    if pd.isna(d["current_delayed_time"]): d["current_delayed_time"] = None
                    d["information_message"] = str(d["stop_order_diff"]) + "전역 " + d["train_status"] if d["stop_order_diff"] >= 1 else "당역 " + d["train_status"]
                    
                    if station_id not in arrival_hashmap:
                        arrival_hashmap[station_id] = [d]
                    else:
                        arrival_hashmap[station_id].append(d)
            
            self.arrival_hashmap = {
                k:[RealtimeRow(**v) for v in values] for k, values in arrival_hashmap.items()
            }
        
    def get_data_by_station_id(self, station_id: int, up: str, down: str) -> RealtimeStation:
        # Create arrival data
        data = {"left": [], "right": []}
        # Get data by id
        realtime_arrival = self.arrival_hashmap[station_id]
        for row in realtime_arrival:
            if row.up_down == 0:
                data[up].append(row)
            else:
                data[down].append(row)
        return RealtimeStation(**data)
    
if __name__ == "__main__":
    logging.basicConfig(filename = "log/test.log",level = logging.INFO)
    
    rp = RealtimeProcess()
    count = 0
    while True:
        rp.op_d = op_date(datetime_ = datetime.now() + timedelta(days=count))
        rp.next_d = rp.op_d + timedelta(days=1)
        rp.op_d_str = rp.op_d.strftime("%Y-%m-%d")
        rp.next_d_str = rp.next_d.strftime("%Y-%m-%d")
        rp.day_code = 9 if check_holiday(rp.op_d) else 8
        logger.info(f"{rp.op_d}: {"Weekday" if rp.day_code == 8 else "Holiday"}")
        
        rp.set_timetable_data()
        
        logger.info(rp.tb["day_code"].unique())
        
        time.sleep(5)
        count += 1