import time
import threading
import logging
from datetime import datetime, timedelta
import warnings

import requests
import pandas as pd

from .utils import op_date, check_holiday, is_next_date
from .db_manager import DBManager
from .timetable_db_manager import TimetableDBManager
from .get_realtime_information import RealtimeInformation
from .data_model import RealtimeRow, RealtimePositionRow, RealtimePosition, RealtimeStation

logger = logging.getLogger("realtime-arrival")

# To save warning outputs to log file.
def save_warning(message, category, filename, lineno, file=None, line=None):
    logger.warning(f"{category.__name__}: {message} ({filename}, line {lineno})")

# When the RuntimeWarnings are raised, save to the logs.
warnings.showwarning = save_warning
warnings.simplefilter("always", RuntimeWarning)

class RealtimeArrival:
    def __init__(self):
        # realtime information
        self.realtime_information = RealtimeInformation()
        # timetable information
        self.timetable_db_manager = TimetableDBManager()
        
        # Realtime Positon data
        self.realtime_position: dict[int, RealtimePosition] = {}
        # Realtime Arrival data
        self.arrival_hashmap: dict[int, list[RealtimeRow]] = {}
        
        # To convert train status code 
        self.train_status = {
            0: "진입", 1: "도착", 2: "출발", 3: "전역출발", 4: "전역진입", 5: "전역도착", 99: "운행중"
        }
        
        # Set operation date
        self.op_d = op_date(datetime_ = datetime.now())
        self.next_d = self.op_d + timedelta(days=1)
        self.op_d_str = self.op_d.strftime("%Y-%m-%d")
        self.next_d_str = self.next_d.strftime("%Y-%m-%d")
        self.day_code = 9 if check_holiday(self.op_d) else 8
        
        # Load static data: timetable data
        self.tb: pd.DataFrame = self._load_timetable_data() 
        self.lines_id_name: dict[int, str] = self._load_line_data() 
        
    def open_http_session(self):
        self.session = requests.Session()
        
    def close_http_session(self):
        self.session.close()
    
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
        
    def _load_line_data(self) -> dict[int, str]:
        # Load line information dict
        data = self.timetable_db_manager.execute("""
            SELECT 
                line_id, line_name 
            FROM lines 
            WHERE line_id < 2000
        """)
        return {d[0]:d[1] for d in data}
    
    def _get_realtime_arrival(self) -> dict[int, list]:
        api_name = "realtimeArrival/ALL"
        requested_at = datetime.now()
        logger.info(f"{api_name} Requested_at: {requested_at}")
        
        # Get realtimeArrival/ALL API
        url_realtimeArrivalAll = self.realtime_information.get_url("realtimeStationArrival/ALL")
        data: list[dict] = self.realtime_information.parse_response(
            self.session.get(url_realtimeArrivalAll, timeout=2))
        
        # New data hashmap
        data_hashmap: dict[int, list] = {}
        # If there is no data
        if data is None: return data_hashmap
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
    
    def _get_realtime_position(self) -> pd.DataFrame:
        api_name = "realtimePosition"
        data = []
        requested_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"{api_name} Requested_at: {requested_at}")
        
        for line_id in self.lines_id_name:
            # Create url
            url = self.realtime_information.get_url(api_name, self.lines_id_name[line_id])
            # Get data and parse response
            tmp = self.realtime_information.parse_response(
                self.session.get(url, timeout=2))
            # Fail to get data
            if tmp is not None:
                data.extend(tmp)
        
        # select using columns
        change_cols = {
            "subwayId": "line_id",
            "subwayNm": "line_name",
            "statnId": "station_id",
            "statnNm": "station_name",
            "trainNo": "train_id",
            "recptnDt": "received_at",
            "updnLine": "up_down",
            "statnTid": "last_station_id",
            "statnTnm": "last_station_name",
            "trainSttus": "train_status",
            "directAt": "express",
            "lstcarAt": "is_last_train"
        }
        
        # convert to dataframe
        rt = pd.DataFrame(data, columns=list(change_cols.keys()))
        # Requested time
        rt["requested_at"] = requested_at
        
        # Error when kyungchun line - kwangwoondae station
        try:
            rt = rt.rename(columns=change_cols).astype({"line_id": "int", "train_id": "string", "station_id": "int", "train_status": "int", "last_station_id": "int"})
        except Exception:
            import traceback
            error = traceback.format_exc()
            logger.error(error)
            # 경춘선 광운대
            mask = (rt["subwayId"] == "1067") & (rt["subwayNm"] == "광운대")
            rt.loc[mask, "statnId"] = "1067080119"
            
            mask = (rt["subwayId"] == "1067") & (rt["statnTnm"] == "광운대")
            rt.loc[mask, "statnTid"] = "1067080119"
            
            # 위 경춘선 광운대 이외의 오류 데이터는 로그에 기록 후 삭제
            error_data = rt[rt["statnId"].isna() | rt["statnTid"].isna()]
            if len(error_data) >= 1:
                logger.warning("There are some error data.")
                logger.warning(error_data.to_dict(orient="records"))
                rt = rt.drop(index = error_data.index)
            
            rt = rt.rename(columns=change_cols).astype({"line_id": "int", "train_id": "string", "station_id": "int", "train_status": "int"})
        
        # Change the train_id of line 2
        mask = (rt["line_id"] == 1002) & (rt["train_id"].str.startswith(("3", "4", "6", "7", "8", "9")))
        rt.loc[mask, "train_id"] = "2" + rt.loc[mask, "train_id"].str[1:]
        
        # Drop prev information
        mask = rt["train_status"].isin([0,1,2])
        rt = rt[mask].reset_index(drop=True)
        
        # rt drop duplicates
        # sort: sortkey ["line_id", "train_id", "received_at"]
        # drop_duplicates: subsetkey ["line_id", "train_id", "station_id"] keep = "last"
        rt = rt.sort_values(["line_id", "train_id", "received_at"]).drop_duplicates(["line_id", "train_id"], keep="last")
        return rt
    
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
        
        data_join["received_at_dt"] = pd.to_datetime(data_join["received_at"], format=datetime_format)
        data_join["arrival_datetime_dt"] = pd.to_datetime(data_join["arrival_datetime"], format=datetime_format)
        data_join["department_datetime_dt"] = pd.to_datetime(data_join["department_datetime"], format=datetime_format) 
        
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
        
        return arrival
    
    def process_realtime_data(self):
        # Open HTTP session
        self.open_http_session()
        
        # 1032, 1077, 1094 data
        arrival_hashmap: dict[int, list] = self._get_realtime_arrival()
        
        realtime_position: pd.DataFrame = self._get_realtime_position()
        arrival: pd.DataFrame = self._calculate_arrival_data(realtime_position)
        
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
        
        arrival = arrival.rename(columns=change_cols).sort_values("stop_order_diff")
        
        # Realtime Position Data
        realtime_position_by_line_id = {}
        for d in realtime_position.to_dict(orient="records"):
            line_id = d["line_id"]
            if line_id not in realtime_position_by_line_id:
                realtime_position_by_line_id[line_id] = [d]
            else:
                realtime_position_by_line_id[line_id].append(d)
        self.realtime_position_df = realtime_position
        self.realtime_position = {
            k:RealtimePosition(place = [RealtimePositionRow(**v) for v in values]) for k, values in realtime_position_by_line_id.items()
        }
        
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
        
        # Close HTTP session
        self.close_http_session()
        
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

class IntervalThread:
    def __init__(self, interval: int):
        self.realtime_arrival = RealtimeArrival()
        self.interval = interval # interval second
        self.is_loop = self.check_time()
        self.t = None
        
    def check_time(self):
        # Maintaining time: 04:50 - 01:30 (tomorrow)
        dt_str_now = datetime.now().strftime("%H:%M:%S")
        return dt_str_now >= "04:50:00" or dt_str_now <= "01:30:00"
        
    def get_data(self):
        self.realtime_db_manager = DBManager("db/realtime.db")
        while True:
            self.is_loop = self.check_time()
            if self.is_loop:
                logger.info("Get realtime data for all stations")
                start = time.time()
                
                # To prevent unexpected thread termination
                # Add error log 
                try:
                    # Process realtime data
                    self.realtime_arrival.process_realtime_data()
                    
                    # Save to db   
                    self.realtime_db_manager.transaction(
                        query = (
                            f"""INSERT INTO realtimes VALUES(
                                :line_id,
                                :station_id,
                                :train_id,
                                :received_at,
                                :up_down,
                                :last_station_id,
                                :train_status,
                                :express,
                                :is_last_train,
                                :requested_at
                                )"""),
                        params = self.realtime_arrival.realtime_position_df[
                            ["line_id", "station_id", "train_id", "received_at", "up_down", "last_station_id", "train_status", "express", "is_last_train", "requested_at"]
                        ].to_dict(orient="records"),
                        many = True
                    )
                except Exception:
                    import traceback
                    err = traceback.format_exc()
                    logger.error(err)

                
                logger.info(f"Runtime {time.time()-start:.5f}s... No of Rows: {len(self.realtime_arrival.arrival_hashmap)}")
                time.sleep(self.interval)
            else:
                # Terminate loop.
                cur_datetime = datetime.now()
                next_start_datetime_str = cur_datetime.date().strftime("%Y-%m-%d") + " 04:50:00" 
                next_start_datetime = datetime.strptime(next_start_datetime_str, "%Y-%m-%d %H:%M:%S")
                next_start_interval = (next_start_datetime - cur_datetime).seconds + 1 # Adding 1 seconds to adjust interval time.
                logger.info(f"Current time: {cur_datetime.strftime("%Y-%m-%d %H:%M:%S")} Loop is terminated. \nAfter {next_start_interval//3600}h {next_start_interval%3600//60}m {next_start_interval%3600%60}s, loop will be restarted.")
                time.sleep(next_start_interval)
                
                logger.info(f"Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. Loop is to be started.")
    
    def checkIsAlive(self):
        # Check thread is alive
        return self.t is not None and self.t.is_alive()
    
    def start(self):
        if not self.checkIsAlive():
            self.t = threading.Thread(target = self.get_data) # Set thread to an attribute
            self.t.start()
            logger.info(f"Thread:{self.t.name} starts to run")
        else:
            logger.info("Thread is already running")
        
    
if __name__ == "__main__":
    # start_total = time.time()
    
    # INTERVAL = 15
    
    # interval_process = IntervalThread(INTERVAL)
    # interval_process.start()
    
    cur_datetime = datetime.now()
    # next_start_datetime_str = cur_datetime.date().strftime("%Y-%m-%d") + " 04:50:00"
    # next_start_datetime = datetime.strptime(next_start_datetime_str, "%Y-%m-%d %H:%M:%S")
    # next_start_interval = (next_start_datetime - cur_datetime)
    # print(next_start_interval.microseconds)
    # print(next_start_interval//3600, next_start_interval%3600//60, next_start_interval%3600%60)