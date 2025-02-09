from datetime import datetime

import requests

from .db_manager import DBManager
from .data_model import Station, RealtimeRow, RealtimeLine, RealtimeStation

""" 
    Realtime API
    요청 1: 역명 -> 도착정보
    요청 2: 호선 -> 위치정보
"""

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
        print(f'The type of params is {type(params)}')


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
            print(f'The response status code is {status_code}')
            
    except Exception as err:
        print('url:', url, flush = True)
        import traceback
        traceback.print_exc()
          
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
        print(f"There is some error. Error code is {json['code']}. {json['message']}")
        data = None
    else:
        error = json[keys[0]]
        if error['code'] == 'INFO-000':
            # If code is 'INFO-000', there is no issue.
            print("Success to get data")
            data = json[keys[1]]
        else:
            print(f"There is some error. Error code is {error['code']}. {error['message']}")
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

def get_realtime_station_data(line_id: int, station_name: str, up_down_to_direction: dict) -> RealtimeStation:
    api_key_db_manager = DBManager("db/api_key.db")
    row = api_key_db_manager.execute("SELECT key FROM api_keys").fetchone()
    key = row[0]
    
    json = get_realtimes_json_by_station_name(key, station_name)
    if json is None:
        return {
            "error": "There is no data"
        }
    realtime_station_data = {"left": [], "right": []}
    for j in json: 
        if int(j["subwayId"]) == line_id:
            # print(j)
            realtime_station_row = RealtimeRow(
                train_id = j["btrainNo"],
                last_station_name = j["bstatnNm"],
                searched_station_name = j["statnNm"],
                cur_station_name = j["arvlMsg3"],
                received_at = j["recptnDt"],
                train_status = convert_train_status(j["arvlCd"]),
                express = 1 if j["btrainSttus"] == "급행" else 0,
                up_down = 0 if j["updnLine"] == "상행" else 1,
                expected_arrival_time = int(j['barvlDt']),
                information_message = j["arvlMsg2"]
            )
            
            realtime_station_data[up_down_to_direction[realtime_station_row.up_down]].append(realtime_station_row)
        
    realtime_station = RealtimeStation(**realtime_station_data)
    return realtime_station

if __name__ == "__main__":
    api_key_db_manager = DBManager("db/api_key.db")
    row = api_key_db_manager.execute("SELECT key FROM api_keys").fetchone()
    key = row[0]
    
    line_name = "신분당선"
    station_name = "응암순환(상선)"
    line_id = "1006"
    
    json = get_realtimes_json_by_line_name(key, line_name)
    
    place = []
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
    
    json = get_realtimes_json_by_station_name(key, station_name)
    row = api_key_db_manager.transaction("UPDATE api_keys SET count = (SELECT count FROM api_keys WHERE key = :key) + 1 WHERE key = :key", {"key": key})
    
    realtime_station_data = {"left": [], "right": []}
    for j in json: 
        if j["subwayId"] == line_id:
            # print(j)
            realtime_station_row = RealtimeRow(
                train_id = j["btrainNo"],
                last_station_name = j["bstatnNm"],
                searched_station_name = j["statnNm"],
                cur_station_name = j["arvlMsg3"],
                received_at = j["recptnDt"],
                train_status = convert_train_status(j["arvlCd"]),
                express = 1 if j["btrainSttus"] == "급행" else 0,
                up_down = 0 if j["updnLine"] == "상행" else 1,
                expected_arrival_time = int(j['barvlDt']),
                information_message = j["arvlMsg2"]
            )
            
            if realtime_station_row.up_down == 0:
                realtime_station_data["left"].append(realtime_station_row)
            else:
                realtime_station_data["right"].append(realtime_station_row)
    
    print("left", len(realtime_station_data["left"]), "right", len(realtime_station_data["right"]))
    
    realtime_station = RealtimeStsation(**realtime_station_data)
    print(realtime_station.left)
    print(realtime_station.right)