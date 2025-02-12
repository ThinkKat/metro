import logging
from datetime import datetime

import requests

from .db_manager import DBManager
from .data_model import Station, RealtimeRow, RealtimeLine, RealtimeStation

""" 
    Realtime API
    요청 1: 역명 -> 도착정보
    요청 2: 호선 -> 위치정보
"""

logger = logging.getLogger("realtimes")

# Make endpoint
def make_endpoint(base_url, params):
    """
    Parameters:
    base_url(str): base_url
    params(list or dict): params of API, 
                          list: path parameters(the order of elements must be checked), 
                          dict: query parameters
    
    Returns:
    url endpoint
    """
    if isinstance(params, list):
        params_str = '/'.join([str(p) for p in params])
        url = f'{base_url}/{params_str}'
        return url
    
    elif isinstance(params, dict):
        params_str = '&'.join([f'{key}={params[key]}' for key in params.key()])
        url = f'{base_url}?{params_str}'
        return url
        
    else:
        logger.error(f'The type of params is {type(params)}')


# GET request to open api 
def request_get(url):
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

def parse_realtimes_response(response):
    """
    Parameters: 
    response (requests.Response) : response for request_get() 
    
    Return: 
    data(json) or None
    """
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
    
def get_realtimes_json_by_station_name(api_key: str, station_name: str):
    base_url = 'http://swopenapi.seoul.go.kr/api/subway'
    params = {
        'key': api_key,
        'data_format': 'json',
        'service_name': 'realtimeStationArrival',
        'start_index': 0,
        'end_index': 1000,
        'line_name': station_name
    }
    
    url = make_endpoint(base_url, list(params.values()))
    
    # Save datetime requested
    requested_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = request_get(url)
    
    # If response is None, errors raised during GET requesting 
    if response is None: return None
    # Parsing response to json
    json = parse_realtimes_response(response)
    
    # If there is no data, return None
    if json is None: return None
    
    return json 

def get_realtimes_json_by_line_name(api_key: str, line_name: str):
    base_url = 'http://swopenapi.seoul.go.kr/api/subway'
    params = {
        'key': api_key,
        'data_format': 'json',
        'service_name': 'realtimePosition',
        'start_index': 0,
        'end_index': 1000,
        'line_name': line_name
    }

    url = make_endpoint(base_url, list(params.values()))
    
    # Save datetime requested
    requested_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response = request_get(url)
    
    # If response is None, errors raised during GET requesting 
    if response is None: return None
    # Parsing response to json
    json = parse_realtimes_response(response)
    
    # If there is no data, return None
    if json is None: return None
    
    return json 

def get_realtimes_all_stations_json(api_key: str):
    endpoint = "http://swopenAPI.seoul.go.kr/api/subway"

    params = {
        'key': api_key,
        'data_format': 'json',
        'service_name': 'realtimeStationArrival/ALL',
    }

    url = make_endpoint(endpoint, list(params.values()))

    response = request_get(url)
    # If response is None, errors raised during GET requesting 
    if response is None: return None
    json = parse_realtimes_response(response)
    
    # If there is no data, return None
    if json is None: return None
    return json 

def convert_train_status(train_status: str) -> str:
    """_summary_

    Args:
        train_status (str): 0:진입, 1:도착, 2:출발, 3:전역출발, 4:전역진입, 5:전역도착, 99:운행중

    Returns:
        str: 
    """
    match train_status:
        case "0":
            return "진입"
        case "1":
            return "도착"
        case "2":
            return "출발"
        case "3":
            return "전역출발"
        case "4":
            return "전역진입"
        case "5":
            return "전역도착"
        case "99":
            return "운행중"    
        case _:
            raise Exception("Wrong Input")
        
def get_realtime_station_json_from_api(station_name: str) -> dict:
    api_key_db_manager = DBManager("db/api_key.db")
    row = api_key_db_manager.execute("SELECT key FROM api_keys").fetchone()
    key = row[0]
    
    json = get_realtimes_json_by_station_name(key, station_name)
    if json is None:
        return {
            "error": "There is no data"
        }
    return json

def get_realtime_all_stations_json_from_api() -> dict:
    api_key_db_manager = DBManager("db/api_key.db")
    row = api_key_db_manager.execute("SELECT key FROM api_keys").fetchone()
    key = row[0]
    
    json = get_realtimes_all_stations_json(key)
    if json is None:
        return {
            "error": "There is no data"
        }
    return json


def get_realtime_line_data(line_name: str) -> RealtimeLine:
    api_key_db_manager = DBManager("db/api_key.db")
    row = api_key_db_manager.execute("SELECT key FROM api_keys").fetchone()
    key = row[0]
    
    json = get_realtimes_json_by_line_name(key, line_name)
    place = []
    if json is None:
        return {
            "error": "There is no data"
        }
    for j in json: 
        realtime_line_row = RealtimeRow(
            train_id = j["trainNo"],
            last_station_name = j["statnTnm"],
            cur_station_name = j["statnNm"],
            received_at = j["recptnDt"],
            train_status = convert_train_status(j["trainSttus"]),
            express = int(j["directAt"]),
            up_down = int(j["updnLine"]),
        )
        place.append(realtime_line_row)
        
    realtime_line = RealtimeLine(place = place)
    return realtime_line
    
def get_realtime_station_data(json: dict, line_id: int, up_down_to_direction: dict, train_ids: list) -> RealtimeStation:
    realtime_station_data = {"left": [], "right": []}
    for j in json: 
        if int(j["subwayId"]) == line_id:
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
                if j["btrainNo"].startswith(("3", "4", "6", "7", "8", "9")):
                    j["btrainNo"] = "2" + j["btrainNo"][1:]
            
            # Remove irrelevant trains using train_id data
            if (line_id != 1032 and line_id != 1077 and line_id != 1094) and j["btrainNo"] not in train_ids: continue
            
            realtime_station_row = RealtimeRow(
                train_id = j["btrainNo"],
                last_station_name = j["bstatnNm"],
                searched_station_name = j["statnNm"],
                cur_station_name = j["arvlMsg3"],
                received_at = j["recptnDt"],
                train_status = convert_train_status(j["arvlCd"]),
                express = 1 if j["btrainSttus"] == "급행" else 0,
                up_down = (int(re.search(r"\d+", j["btrainNo"]).group(0)) % 2 == 1) * 1, # 열차번호를 활용해서 상하행 파악
                expected_arrival_time = int(j['barvlDt']),
                information_message = j["arvlMsg2"]
            )
        
            realtime_station_data[up_down_to_direction[realtime_station_row.up_down]].append(realtime_station_row)
        
    realtime_station = RealtimeStation(**realtime_station_data)
    return realtime_station


if __name__ == "__main__":
    pass