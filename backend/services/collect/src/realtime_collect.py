import time
from datetime import datetime

import requests
import pandas as pd

from .realtime_api import RealtimeAPI

class RealtimeCollect:
    def __init__(self):
        self.realtime_api = RealtimeAPI()
        # HTTP session
        self.session = requests.Session()
        # Line id : name dict
        self.line_id_names: dict[int, str] = self._load_line_data() 
        
        # Save Data
        self.realtime_arrival_all: list[dict]|None = None
        self.realtime_position: pd.DataFrame|None = None
        
    def _load_line_data(self) -> dict[int, str]:
        
        # Load line information dict
        # TODO: Connect to DB and load line information dynamically.
        data = {
            1001: "1호선",
            1002: "2호선",
            1003: "3호선",
            1004: "4호선",
            1005: "5호선",
            1006: "6호선",
            1007: "7호선",
            1008: "8호선",
            1009: "9호선",
            1032: "GTX-A",
            1063: "경의중앙선",
            1065: "공항철도",
            1067: "경춘선",
            1075: "수인분당선",
            1077: "신분당선",
            1081: "경강선",
            1092: "우이신설선",
            1093: "서해선",
            1094: "신림선"
        }
        
        return data
    
    def _get_realatime_arrival_all_data(self) -> list[dict]|None:
        """ Requests realtimeArrival
            TODO: Change api_name variable to an environment variable 
        """
        api_name = "realtimeStationArrival/ALL"
        url = self.realtime_api.get_url(api_name)
        response = self.session.get(url, timeout=2)
        data = self.realtime_api.parse_response(response)
        
        return data
    
    def _get_realtime_position_data(self) -> list[dict]|None:
        """ Requests realtime Position 
            TODO: Change api_name variable to an environment variable 
        """
        api_name = "realtimePosition"
        data = []
        for line_id in self.line_id_names:
            line_name = self.line_id_names[line_id]
            url = self.realtime_api.get_url(api_name, line_name)
            response = self.session.get(url, timeout=2)
            tmp = self.realtime_api.parse_response(response)
            
            if tmp is not None:
                data.extend(tmp)
        return data
    
    def _preprocess_realtime_position(self, data: list[dict]) -> pd.DataFrame:
        """
            Processing realtime position data.
            1. Change the names of columns
            2. Handle Exception: 데이터 자체 오류
            3. Change the train id of line 2
            4. Drop prev information
        """
        
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
        
        # Convert dtypes
        dtype = {
            "line_id": "int", 
            "line_name": "string",
            "station_id": "int", 
            "station_name": "string",
            "train_id": "string", 
            "received_at": "string", 
            "up_down": "int",
            "last_station_id": "int",
            "last_station_name": "string",
            "train_status": "int",
            "express": "int",
            "is_last_train": "int"
        }
        
        # convert to dataframe
        rt = pd.DataFrame(data, columns=list(change_cols.keys()))
        
        # Error when kyungchun line - kwangwoondae station
        try:
            rt = rt.rename(columns=change_cols).astype(dtype)
        except Exception:
            import traceback
            
            # 경춘선 광운대
            mask = (rt["subwayId"] == "1067") & (rt["statnNm"] == "광운대")
            rt.loc[mask, "statnId"] = "1067080119"
            
            mask = (rt["subwayId"] == "1067") & (rt["statnTnm"] == "광운대")
            rt.loc[mask, "statnTid"] = "1067080119"
            
            mask = (rt["subwayId"] == "1067") & (rt["statnNm"] == "용산")
            rt.loc[mask, "statnId"] = "1063075110" # 경의중앙선 용산역 코드
            
            # 위 경춘선 광운대 이외의 오류 데이터는 로그에 기록 후 삭제
            error_data = rt[rt["statnId"].isna() | rt["statnTid"].isna()]
            if len(error_data) >= 1:
                error = traceback.format_exc()
                # logger.error(error)
                # logger.warning("There are some error data.")
                # logger.warning(error_data.to_dict(orient="records"))
                rt = rt.drop(index = error_data.index)
            
            rt = rt.rename(columns=change_cols).astype({"line_id": "int", "train_id": "string", "station_id": "int", "train_status": "int"})
        
        # Change the train_id of line 2
        mask = (rt["line_id"] == 1002) & (rt["train_id"].str.startswith(("3", "4", "6", "7", "8", "9")))
        rt.loc[mask, "train_id"] = "2" + rt.loc[mask, "train_id"].str[1:]
        
        # Drop prev information
        mask = rt["train_status"].isin([0,1,2])
        rt = rt[mask].reset_index(drop=True)
        
        """
            Drop duplicates
            sort: sortkey ["line_id", "train_id", "received_at"]
            drop_duplicates: subsetkey ["line_id", "train_id", "station_id"] keep = "last"
        """
        rt = rt.sort_values(["line_id", "train_id", "received_at"]).drop_duplicates(["line_id", "train_id"], keep="last")
        return rt
    
    def collect_realtime_data(self):
        """
            realtime
        """
        
        # logger.debug(f"Process realtime data {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        start = time.time()
        
        # Get realtimeArrival/ALL data
        requested_at_arrival_all = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # logger.debug(f"realtimeArrival/ALL Requested_at: {requested_at_arrival_all}")
        self.realtime_arrival_all = self._get_realatime_arrival_all_data()
        
        # Get realtimeArrival
        requested_at_position= datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # logger.debug(f"realtimePosition Requested_at: {requested_at_position}")
        data = self._get_realtime_position_data()
        if data is not None:
            self.realtime_position = self._preprocess_realtime_position(data)
            self.realtime_position["requested_at"] = requested_at_position
        
        # logger.debug(f"Process data {time.time()-start:05f}s...")
        # Close session
        self.session.close()