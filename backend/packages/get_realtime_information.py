import logging
from datetime import datetime

import requests

from .db_manager import DBManager
from .data_model import RealtimeRow, RealtimeLine, RealtimeStation

""" 
    Realtime API
    요청 1: 역명 -> 도착정보
    요청 2: 호선 -> 위치정보
    
    1. utils (Functions to use after requesting to realtime data api)
      - parse_realtimes_response
    2. request to realtime data api
      - make_endpoint
      - request_get
    3. postprocess
"""

logger = logging.getLogger("realtimes")

# GET request to open api 
def request_get(url: str) -> requests.models.Response|None:
    """ Get the data using api
    
    Parameters:
    url: str, api endpoint
    
    Returns:
    <class 'requests.models.Response'> or None 
    
    """
    try:
        response = requests.get(url, timeout = 2)
        status_code = response.status_code
        
        # check the status code
        if status_code == 200:
            # status_code == 200: OK
            return response
        else :
            # status code != 200 is error
            logger.error(f'The response status code is {status_code}')
            
    except Exception as err:
        logger.error('url:', url)
        import traceback
        tb = traceback.format_exc()
        logger.error(tb)
          
    # Return the None when the status code is not 200
    return None

class RealtimeInformation:
    def __init__(self):
        self.api_key = self.get_key()
        self.base_url = 'http://swopenapi.seoul.go.kr/api/subway'
        self.train_status = {
            "0": "진입", "1": "도착", "2": "출발", "3": "전역출발", "4": "전역진입", "5": "전역도착", "99": "운행중"
        }
    
    def get_key(self) -> str:
        api_key_db_manager = DBManager("db/api_key.db")
        row = api_key_db_manager.execute("SELECT key FROM api_keys").fetchone()
        return row[0]
    
    # Get json data 
    def get_realtime_data(self, api_name: str, name: str = None) -> dict|None:
        url = self.get_url(api_name, name)
        response = self.request_to_api(url)
        data = self.parse_response(response)
        return data        
    
    # Get endpoint
    def get_url(self, api_name: str, name: str = None) -> str:
        if api_name == "realtimePosition": return f"{self.base_url}/{self.api_key}/json/realtimePosition/0/1000/{name}"
        elif api_name == "realtimeStationArrival": return f"{self.base_url}/{self.api_key}/json/realtimeStationArrival/0/1000/{name}"
        elif api_name == "realtimeStationArrival/ALL": return f"{self.base_url}/{self.api_key}/json/realtimeStationArrival/ALL"
        else: raise Exception(f"There isn't no api named {api_name}")
    
    def request_to_api(self, url: str) -> requests.models.Response|None:
        response = request_get(url)
        return response
    
    def parse_response(self, response: requests.models.Response|None) -> dict|None:
        """
        Parameters: 
        response (requests.Response) : response for request_get() 
        
        Return: 
        data(json) or None
        """
        # response error
        if response is None: return None 
        
        # Check errorMessage
        json = response.json()
        keys = list(json.keys())

        if 'code' in keys:
            logger.error(f"There is some error. Error code is {json['code']}. {json['message']}")
            data = None
        else:
            error = json[keys[0]]
            if error['code'] == 'INFO-000':
                # If code is 'INFO-000', there is no issue.
                logger.info("Success to get data")
                data = json[keys[1]]
            else:
                logger.error(f"There is some error. Error code is {error['code']}. {error['message']}")
                data = None

        return data
        
    def postprocess_realtime_position(self, data: list[dict]|None) -> RealtimeLine:
        if data is None: return RealtimeLine(place = [])
        
        return RealtimeLine(
            place = [
                RealtimeRow(
                    train_id = d["trainNo"],
                    last_station_name = d["statnTnm"],
                    cur_station_name = d["statnNm"],
                    received_at = d["recptnDt"],
                    train_status = self.train_status[d["trainSttus"]],
                    express = int(d["directAt"]),
                    up_down = int(d["updnLine"]),
                )
                for d in data
            ]
        )

    def postprocess_realtime_station(self, data: list[dict]|None, line_id: int, up_down_to_direction: dict, train_ids: list) -> RealtimeStation:
        realtime_station_data = {"left": [], "right": []}
        if data is None: return RealtimeStation(**realtime_station_data)
        
        for d in data: 
            """
                도착정보 데이터 (realtimeStationArrival) 오류 문제
                1. 2호선 상하행 문제(모든 열차가 같은 방향으로 표시됨.)
                2. 해당 역을 지나지 않는 열차도 표시됨. (예: 1호선 상행열차(서울->청량리 방향) 중 청량리가 종착역인 열차의 정보가 회기역에서 표시됨.)
                3. 2호선 열차번호 문제 (2로 시작해야할 열차번호가 3,4,6,7,8,9로 시작함. 1-성수지선과 5-신정지선는 옳바른 데이터.) 
                
                1번에 대한 문제 해결 방법: 상하행 파악 로직을 추가. (열차번호를 통해 파악 가능. 열차번호가 짝수인 경우 상행, 홀수인 경우 하행. 신분당선, GTX-A)
                2번에 대한 문제 해결 방법: 시간표의 열차번호 목록을 활용하여 관련 없는 열차 제거.
                3번에 대한 문제 해결 방법: 관련없는 열차를 제거하기 전 2호선의 잘못된 열차번호를 수정하는 로직 추가
            """
            import re
            
            # 3번 문제: 2호선 잘못된 열차번호
            if line_id == 1002: 
                if d["btrainNo"].startswith(("3", "4", "6", "7", "8", "9")):
                    d["btrainNo"] = "2" + d["btrainNo"][1:]
            
            # Remove irrelevant trains using train_id data
            if (line_id != 1032 and line_id != 1077 and line_id != 1094) and d["btrainNo"] not in train_ids: continue
            
            # 2호선 열차는 열차번호를 활용해서 상하행 파악
            if line_id == 1002:
                up_down = (int(re.search(r"\d+", d["btrainNo"]).group(0)) % 2 == 1) * 1, 
            else:
                up_down = 0 if d["updnLine"] == "상행" else 1
            
            realtime_station_row = RealtimeRow(
                train_id = d["btrainNo"],
                last_station_name = d["bstatnNm"],
                searched_station_name = d["statnNm"],
                cur_station_name = d["arvlMsg3"],
                received_at = d["recptnDt"],
                express = 1 if d["btrainSttus"] == "급행" else 0,
                train_status = self.train_status[d["arvlCd"]],
                up_down = up_down,
                expected_arrival_time = int(d['barvlDt']),
                information_message = d["arvlMsg2"]
            )
                
            realtime_station_data[up_down_to_direction[realtime_station_row.up_down]].append(realtime_station_row)
    
        return RealtimeStation(**realtime_station_data)


if __name__ == "__main__":
    pass