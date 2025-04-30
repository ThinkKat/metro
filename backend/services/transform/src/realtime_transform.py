import logging
import traceback
import time
import re
from datetime import datetime, timedelta
from multiprocessing.connection import Client

import pandas as pd
from sqlalchemy import create_engine, select, text # TODO: Substitue to repository modules
from sqlalchemy.orm import Session

from .utils import op_date, check_holiday, is_next_date
# TODO: Remove data_model. Substitute to python object (dict)
from .data_model import RealtimeRow, RealtimePositionRow, RealtimePosition, RealtimeStation 
from .config import POSTGRESQL_METRO_DB_URL, UDS_ADDRESS 

# logger = logging.getLogger("realtime-process")

class RealtimeTransform:
    def __init__(self, address = UDS_ADDRESS):
        self.address = address # TODO: Change to Communication Handler
        
        # To convert train status code 
        self.train_status = {
            0: "진입", 1: "도착", 2: "출발", 3: "전역출발", 4: "전역진입", 5: "전역도착", 99: "운행중"}
        
        # Arrival line
        self.arrival_line = [1077]
        
        # Connect to socket pipe
        self.connect()
        
        # Set data, op_date, timetable data
        self.init()
        
    def init(self):

        # Realtime data from interval collection worker
        self.init_data()
        # Set operational date
        self.set_op_date()
        # Load static data: timetable data
        self.set_timetable_data()
        
        logger.info("Initialize realtime data, operational date, and timetable data")
    
    def connect(self):
        """
        TODO: Divide to communication handler
        """
        # Client
        try:
            self.client = Client(self.address)
            logger.info("Connected to listener")
        except ConnectionRefusedError:
            # This excpetion is raised when the pipe isn't opening.
            logger.error(traceback.format_exc())
            time.sleep(5)
            self.client = None
        except FileNotFoundError:
            # This exception is raised when the uds(AF_UNIX) files doesn't exists
            logger.error(traceback.format_exc())
            time.sleep(5)
            self.client = None
        except Exception:
            logger.error(traceback.format_exc())
            self.client = None
    
    def init_data(self):
        """
        TODO: Divide to communication handler
        """
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
        """
        TODO: Divide to Repository
        """
        # load timetable data
        # using self attributes
        db_url = f"postgresql://{POSTGRESQL_METRO_DB_URL}"
        engine = create_engine(db_url)
        with Session(engine) as session:
            # load timetable data
            # using self attributes
            data = session.execute(text("""
                    SELECT 
                        tb.*,
                        s.station_id,
                        s.station_name
                    FROM timetables tb
                    INNER JOIN stations s
                    ON tb.line_id = s.line_id
                    AND tb.station_public_code = s.station_public_code
                    WHERE (tb.updated_at <= :op_date AND (tb.end_date > :op_date OR tb.end_date IS NULL))
                    AND tb.day_code = :day_code
                """),
                {"op_date": self.op_d_str, "day_code": self.day_code}
            )
        tb = pd.DataFrame([r for r in data.fetchall()], columns = data.keys())
        tb = tb.drop(columns = ["train_id"])
        
        # Convert time to datetime
        tb["arrival_datetime"] = tb["arrival_time"]
        tb.loc[~tb["arrival_time"].isna(), "arrival_datetime"] = tb.loc[~tb["arrival_time"].isna(),"arrival_time"].astype("string").apply(lambda x : self.next_d_str + " " + x if is_next_date(x) else self.op_d_str + " " + x)
        tb["department_datetime"] = tb["department_time"]
        tb.loc[~tb["department_time"].isna(), "department_datetime"] = tb.loc[~tb["department_time"].isna(), "department_time"].astype("string").apply(lambda x : self.next_d_str + " " + x if is_next_date(x) else self.op_d_str + " " + x)
        
        return tb
    
    def _process_arrival_all_data(self, data: list[dict]) -> dict[int, list]:
        """
            Transform arrival data
        """
        # New data hashmap
        data_hashmap: dict[int, list] = {}
        for row in data:
            # Filtering necessary data
            # Necessary Line data: 1032, 1077, 1094
            if int(row["subwayId"]) not in self.arrival_line: continue
            
            station_id = int(row["statnId"])
            
            # Extract necessary attributes
            train_status = self.train_status[int(row["arvlCd"])]
            information_message = row["arvlMsg2"]
            """
                2 types of message 
                1. OO OO 
                    The first type of message is composed to 2 words splited by space.
                    예: 당역 도착, 전역 출발
                    Spliting: ["당역", "도착"], ["전역", "출발"]
                2. [n]OO OO (current_station_name)
                    The second type of message is composed to 3 words splited by space.
                    예: [2]번째 전역 (양재시민의 숲)
                    Spliting: ["[2]번쩨", "전역", "(양재시민의 숲)"]
            """
            partial_message = information_message.split(maxsplit = 2)
            try:
                if len(partial_message) == 2:
                    if partial_message[0] == "당역":
                        stop_order_diff = 0
                    else:
                        stop_order_diff = 1
                    information_message = f"{stop_order_diff}전역 {partial_message[1]}"
                else:
                    stop_order_diff = int(re.search(r'[0-9]+', partial_message[0]).group(0))
                    information_message = f"{stop_order_diff}전역"
            except:
                logger.error(traceback.format_exc())
                stop_order_diff = None
            
            new_row = {
                "train_id": row["btrainNo"],
                "last_station_name": row["bstatnNm"],
                "searched_station_name": row["statnNm"],
                "cur_station_name": row["arvlMsg3"],
                "received_at": row["recptnDt"],
                "express": 1 if row["btrainSttus"] == "급행" else 0,
                "train_status": train_status,
                "up_down": 0 if row["updnLine"] == "상행" else 1,
                "expected_left_time": int(row["barvlDt"]),
                "stop_order_diff": stop_order_diff,
                "information_message": information_message
            }
            
            if station_id not in data_hashmap:
                data_hashmap[station_id] = [new_row]
            else:
                data_hashmap[station_id].append(new_row)
        return data_hashmap
    
    def _calculate_delay_time(self, realtime_position: pd.DataFrame) -> pd.DataFrame:
        """
            Calculate delay time
            TODO: Compare to Delay Calculator
        """
        
        # Data join
        data_join = pd.merge(
            realtime_position[["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at"]],
            self.tb,
            left_on = ["line_id", "train_id", "station_id"],
            right_on = ["line_id", "realtime_train_id", "station_id"],
            how = "left" # 정보 파싱 가능한 데이터만
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
        return data_join
    
    def get_delay_data(self, realtime_position: pd.DataFrame) -> pd.DataFrame:
        # public method of getting delay data
        return self._calculate_delay_time(realtime_position)
    
    def _calculate_arrival_data(self, realtime_position: pd.DataFrame) -> pd.DataFrame:
        """
            Dependency: self._calculate_delay_time()
            Calculate arrival information after calculating delay time 
        """
        
        # Join next timetable data
        # Next suffix means searched station.
        arrival = pd.merge(
            realtime_position,
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
        
        change_types = {
            "searched_station_department_time": "string",
            "searched_station_arrival_time": "string",
        }
        
        # Sort values bt stop_order_diff
        arrival = arrival.rename(columns=change_cols).astype(change_types).sort_values("stop_order_diff")
        
        return arrival
    
    def process_realtime_data(self, position_data: pd.DataFrame|None, arrival_data: list[dict]|None):
        """ Union arrival data and arrival/all data. 


        Args:
            position_data (pd.DataFrame | None): _description_
            arrival_data (list[dict] | None): _description_
        """
        
        
        if position_data is not None:
            # Convert Type
            position_data["received_at"] = position_data["received_at"].astype("string")
            
            delay: pd.DataFrame = self._calculate_delay_time(position_data)
            arrival: pd.DataFrame = self._calculate_arrival_data(delay)
            
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
                if not d["line_id"] in self.arrival_line:
                    station_id = d["searched_station_id"]
                    d["train_status"] = self.train_status[d["train_status"]]
                    if pd.isna(d["current_delayed_time"]): d["current_delayed_time"] = None
                    d["information_message"] = str(int(d["stop_order_diff"])) + "전역 " + d["train_status"] if d["stop_order_diff"] >= 1 else "당역 " + d["train_status"]
                    
                    if station_id not in arrival_hashmap:
                        arrival_hashmap[station_id] = [d]
                    else:
                        arrival_hashmap[station_id].append(d)
            
            self.arrival_hashmap = {
                k:[RealtimeRow(**v) for v in values] for k, values in arrival_hashmap.items()
            }
        
    def get_data_by_station_id(self, station_id: int, up: str, down: str) -> RealtimeStation:
        """Get arrival data by station_id 
           TODO: Remove parameters up, down, only

        Args:
            station_id (int): _description_
            up (str): _description_
            down (str): _description_

        Returns:
            RealtimeStation: _description_
        """
        
        # Create arrival data
        data = {"left": [], "right": []}
        # Get data by id
        realtime_arrival = self.arrival_hashmap[station_id]
        
        # up: "left_direction", down: "right_direction"
        for row in realtime_arrival:
            if row.up_down == 0:
                data[up.split("_")[0]].append(row)
            else:
                data[down.split("_")[0]].append(row)
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