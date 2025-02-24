import time
import threading
from datetime import datetime, timedelta

import pandas as pd

from .utils import op_date, check_holiday, is_next_date
from .timetable_db_manager import TimetableDBManager
from .get_realtime_information import RealtimeInformation
from .data_model import RealtimeRow, RealtimeStation

class RealtimeArrival:
    def __init__(self):
        # realtime information
        self.realtime_information = RealtimeInformation()
        # timetable information
        self.timetable_db_manager = TimetableDBManager()
        
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
        print(f"{api_name} Requested_at: {requested_at}")
        
        # Get realtimeArrival/ALL API
        data: list[dict] = self.realtime_information.get_realtime_data("realtimeStationArrival/ALL")
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
    
    def _get_realtime_position(self) -> pd.DataFrame:
        api_name = "realtimePosition"
        data = []
        requested_at = datetime.now()
        print(f"{api_name} Requested_at: {requested_at}")
        
        for line_id in self.lines_id_name:
            if not line_id in [1032, 1077, 1094]:
                tmp = self.realtime_information.get_realtime_data(api_name, self.lines_id_name[line_id])
                # Fail to get data
                if tmp is not None:
                    data.extend(tmp)
                time.sleep(0.03)
        
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
        data_join.loc[data_join["train_status"]<=1, "delayed_time"] = (pd.to_datetime(data_join["received_at"]) - pd.to_datetime(data_join["arrival_datetime"])).dt.total_seconds()
        data_join.loc[data_join["train_status"]==2, "delayed_time"] = (pd.to_datetime(data_join["received_at"]) - pd.to_datetime(data_join["department_datetime"])).dt.total_seconds()
        data_join.loc[data_join["train_status"]==0, "delayed_time"] += 30 # 열차 접근 상태 보정
        
        # Join next timetable data
        arrival = pd.merge(
            data_join,
            self.tb,
            left_on = ["line_id", "train_id"],
            right_on = ["line_id", "realtime_train_id"],
            how = "inner",
            suffixes=("","_next")
        )
        mask = (arrival["stop_no"] <= arrival["stop_no_next"]) & (arrival["express_non_stop"] == 0)
        arrival = arrival[mask]
        
        arrival["diff"] = arrival["stop_no_next"] - arrival["stop_no"]
        arrival["expected_arrival_time"] = pd.to_datetime(arrival["arrival_datetime_next"]) + pd.to_timedelta(arrival["delayed_time"], unit="s")
        arrival["expected_arrival_time"] = arrival["expected_arrival_time"].astype("string")
        
        return arrival
    
    def process_arrival_data(self):
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
        }
        
        arrival = arrival.rename(columns=change_cols).sort_values("stop_order_diff")
        
        # Add arrival data
        for d in arrival.to_dict(orient="records"):
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

class IntervalProcess:
    def __init__(self, interval: int):
        self.realtime_arrival = RealtimeArrival()
        self.interval = interval # interval second
        self.is_loop = self.check_time()
        
    def check_time(self):
        # Maintaining time: 04:50 - 01:30 (tomorrow)
        dt_str_now = datetime.now().strftime("%H:%M:%S")
        return dt_str_now >= "04:50:00" or dt_str_now <= "01:30:00"
        
    def get_data(self):
        while True:
            self.is_loop = self.check_time()
            if self.is_loop:
                print("Get realtime data for all stations")
                self.realtime_arrival.process_arrival_data()
                print(len(self.realtime_arrival.arrival_hashmap))
            time.sleep(self.interval)
            
    def start(self):
        t = threading.Thread(target = self.get_data)
        t.start()


if __name__ == "__main__":
    # start_total = time.time()
    
    INTERVAL = 15
    
    interval_process = IntervalProcess(INTERVAL)
    interval_process.start()
    
    