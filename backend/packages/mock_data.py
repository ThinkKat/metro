# 회기역
mock_data = [
    {
        "line": {
            "line_id": 1001,
            "line_color": "0052A4",
            "line_name": "1호선"      
        },
        "station": {
            "station_public_code": "123",
            "station_name": "회기",
            "station_id": 1001000133
        },
        "adjacent_stations": {
            "left": [
                {
                    "station_public_code": "122",
                    "station_name": "외대앞",
                    "up_down": 1
                }
            ],
            "right": [
                {
                    "station_public_code": "124",
                    "station_name": "청량리",
                    "up_down": 0
                }
            ],
        }
        "transfer_lines": [
            {
                "line_id": 1063,
                "line_color": "77C4A3",
                "line_name": "경의중앙선"      
            },
            {
                "line_id": 1067,
                "line_color": "178C72",
                "line_name": "경춘선"      
            },
        ],
        "realtimes": {
            "left": [
                
            ],
            "right": [
                
            ]
        },
        "timetables": {
            "weekday": {
                "left": [
                    {
                        "train_id": "K802",
                        "first_station_name": "구로",
                        "last_station_name": "동두천",
                        "arrival_time": "05:42:00", 
                        "department_time": "05:42:30",
                        "express": 0,
                    },
                    {
                        "train_id": "S902",
                        "first_station_name": "서울역",
                        "last_station_name": "의정부",
                        "arrival_time": "05:45:30", 
                        "department_time": "05:46:00",
                        "express": 0,
                    },
                ]    
                "right": [
                    {
                        "train_id": "K11",
                        "first_station_name": "광운대",
                        "last_station_name": "인천",
                        "arrival_time": "05:08:00", 
                        "department_time": "05:08:30",
                        "express": 0,
                    },
                    {
                        "train_id": "K13",
                        "first_station_name": "창동",
                        "last_station_name": "인천",
                        "arrival_time": "05:15:00", 
                        "department_time": "05:15:30",
                        "express": 0,
                    },
                ],
            },
            "saturday": {
                "left": [
                    {
                        "train_id": "K802",
                        "first_station_name": "구로",
                        "last_station_name": "동두천",
                        "arrival_time": "05:42:00", 
                        "department_time": "05:42:30",
                        "express": 0,
                    },
                    {
                        "train_id": "S902",
                        "first_station_name": "서울역",
                        "last_station_name": "의정부",
                        "arrival_time": "05:45:30", 
                        "department_time": "05:46:00",
                        "express": 0,
                    },
                ]    
                "right": [
                    {
                        "train_id": "K7",
                        "first_station_name": "광운대",
                        "last_station_name": "인천",
                        "arrival_time": "05:08:00", 
                        "department_time": "05:08:30",
                        "express": 0,
                    },
                    {
                        "train_id": "K9",
                        "first_station_name": "광운대",
                        "last_station_name": "인천",
                        "arrival_time": "05:20:00", 
                        "department_time": "05:20:30",
                        "express": 0,
                    },
                ],
            },
            "holiday": {
                "left": [
                    {
                        "train_id": "K802",
                        "first_station_name": "구로",
                        "last_station_name": "동두천",
                        "arrival_time": "05:42:00", 
                        "department_time": "05:42:30",
                        "express": 0,
                    },
                    {
                        "train_id": "S902",
                        "first_station_name": "서울역",
                        "last_station_name": "의정부",
                        "arrival_time": "05:45:30", 
                        "department_time": "05:46:00",
                        "express": 0,
                    },
                ]    
                "right": [
                    {
                        "train_id": "K7",
                        "first_station_name": "광운대",
                        "last_station_name": "인천",
                        "arrival_time": "05:08:00", 
                        "department_time": "05:08:30",
                        "express": 0,
                    },
                    {
                        "train_id": "K9",
                        "first_station_name": "광운대",
                        "last_station_name": "인천",
                        "arrival_time": "05:20:00", 
                        "department_time": "05:20:30",
                        "express": 0,
                    },
                ],
            },     
        }
    }
]