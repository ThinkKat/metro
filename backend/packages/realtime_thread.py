import threading
import time
from datetime import datetime

from packages.get_realtime_information import get_realtime_all_stations_json_from_api

class IntervalProcess:
    def __init__(self, interval: int):
        self.interval = interval # interval second
        self.data = None
        self.data_hashmap = None
        self.is_loop = self.check_time()
        
    def check_time(self):
        # Maintaining time: 04:50 - 01:30 (tomorrow)
        dt_str_now = datetime.now().strftime("%H:%M:%S")
        return dt_str_now >= "04:50:00" or dt_str_now <= "01:30:00"
        
    def get_data(self):
        while self.is_loop:
            print(f"------------------{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}------------------")
            start = time.time()
            self.data = get_realtime_all_stations_json_from_api()

            # New data hashmap
            new_data_hashmap = {}
            for d in self.data:
                station_id = int(d["statnId"])
                if station_id not in new_data_hashmap:
                    new_data_hashmap[station_id] = [d]
                else:
                    new_data_hashmap[station_id].append(d)
            self.data_hashmap = new_data_hashmap
                    
            self.is_loop = self.check_time()
            time.sleep(self.interval)
            
    def start(self):
        t = threading.Thread(target = self.get_data)
        t.start()
        print(t.ident)
        
            
if __name__ == "__main__":
    ip = IntervalProcess(15)
    ip.start()