import os

import pandas as pd

from packages.delay_calculator import DelayCalculator

file_dir = "/Volumes/Backup Plus/thinkcat/Metro/processed_realtimes"
files = [f for f in os.listdir(file_dir) if "csv" in f and "all_stations" not in f]
files.sort()
total_delay_data = []
dtype = {
    "line_id":"int",
    "station_id":"int",
    "train_id":"string",
    "received_at":"string",
    "up_down":"int",
    "last_station_id":"int",
    "train_status":"int",
    "express":"int",
    "is_last_train":"int",
    "requested_at":"string"
}
for f in files:
    tmp = pd.read_csv(f"{file_dir}/{f}", dtype=dtype)
    op_date = f[0:10]
    print(f)
    dc = DelayCalculator(op_date)
    
    delay_data = dc._calculate_delayed_time(tmp)
    delay_data["op_date"] = op_date
    delay_data["day_code"] = dc.day_code
    delay_data = delay_data.astype({"first_last": "Int16", "stop_no": "Int16"})
    delay_data["stop_no"] = delay_data["stop_no"].fillna(-1)
    # delay_data["delayed_time"] = delay_data["delayed_time"].dt.total_seconds()
    
    # Insert delay data
    usecols = ["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at", "day_code", "first_last", "stop_no", "delayed_time", "op_date"]
    total_delay_data.append(delay_data[usecols])

total_delay = pd.concat(total_delay_data)
total_delay.to_csv("total_delay.csv", index=False)