import logging

import requests

from .config import API_KEY_DB_PATH
from .db_manager import DBManager

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

class RealtimeInformation:
    def __init__(self):
        self.api_key = self.get_key()
        self.base_url = 'http://swopenapi.seoul.go.kr/api/subway'

    def get_key(self) -> str:
        api_key_db_manager = DBManager(API_KEY_DB_PATH)
        row = api_key_db_manager.execute("SELECT key FROM api_keys").fetchone()
        return row[0]    
    
    # Get endpoint
    def get_url(self, api_name: str, name: str = None) -> str:
        if api_name == "realtimePosition": return f"{self.base_url}/{self.api_key}/json/realtimePosition/0/1000/{name}"
        elif api_name == "realtimeStationArrival": return f"{self.base_url}/{self.api_key}/json/realtimeStationArrival/0/1000/{name}"
        elif api_name == "realtimeStationArrival/ALL": return f"{self.base_url}/{self.api_key}/json/realtimeStationArrival/ALL"
        else: raise Exception(f"There isn't no api named {api_name}")
    
    def parse_response(self, response: requests.models.Response|None) -> dict|None:
        """
        Parameters: 
        response (requests.Response) : response for request_get() 
        
        Return: 
        data(json) or None
        """
        # HTTP error
        try:
            status_code = response.status_code
            
            # check the status code
            if status_code != 200:
                # status code != 200 is error
                logger.error(f'The response status code is {status_code}')
                
        except Exception as err:
            import traceback
            tb = traceback.format_exc()
            logger.error(tb)
            return None
        
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
                # logger.info("Success to get data")
                data = json[keys[1]]
            else:
                logger.error(f"There is some error. Error code is {error['code']}. {error['message']}")
                data = None

        return data


if __name__ == "__main__":
    import time
    
    ri = RealtimeInformation()
    line_names = [
        "1호선", "2호선", "3호선", "4호선", "5호선", "6호선", "7호선", "8호선", "9호선",
        "GTX-A", "경의중앙선", "공항철도", "경춘선", "수인분당선", 
        "신분당선", "경강선", "우이신설선", "서해선", "신림선"
    ]
    
    start = time.time()
    for line_name in line_names:
        url = ri.get_url("realtimePosition", line_name)
        response = requests.get(url)
        data = ri.parse_response(response)
    print(f"Without session: {time.time() - start:.5f}s...")
    
    
    start = time.time()
    with requests.session() as session:
        for line_name in line_names:
            url = ri.get_url("realtimePosition", line_name)
            response = session.get(url, timeout=2)
            data = ri.parse_response(response)
    print(f"With session: {time.time() - start:.5f}s...")