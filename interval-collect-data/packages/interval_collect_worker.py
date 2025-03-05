import threading
import time
import logging
import traceback
import os
import sqlite3
from datetime import datetime

from .ipc_listeners import IPCListner
from .config import REALTIME_SAVE_DB_PATH, PREV_REALTIME_SAVE_DB_PATH
from .realtime_collect import RealtimeCollect

logger = logging.getLogger("realtime-collect")

class IntervalCollectWorker:
    def __init__(self, interval: int):
        self.interval = interval
        self.run_loop = self.check_time()
        self.listener = IPCListner()
        self.t = None # Set thread to an attribute.
    
    def check_thread_is_alive(self):
        return self.t is not None and self.t.is_alive()
    
    def check_time(self):
        # Maintaining time: 04:50 - 01:30 (tomorrow)
        dt_str_now = datetime.now().strftime("%H:%M:%S")
        return dt_str_now >= "04:50:00" or dt_str_now <= "01:30:00"
    
    def interval_work(self):
        # Open ipc listener
        t = threading.Thread(target = self.listener.start)
        t.start()
                
        # Realtime Collect Module
        realtime_collect = RealtimeCollect()
        
        while True:
            self.run_loop = self.check_time()
            if self.run_loop:
                try:
                    # Process data
                    realtime_collect.collect_realtime_data()
                    
                    # Send data
                    self.listener.set_data([realtime_collect.realtime_position, realtime_collect.realtime_arrival_all])
                    
                    # Save data
                    realtime_conn = sqlite3.connect(REALTIME_SAVE_DB_PATH)
                    realtime_cur = realtime_conn.cursor()
                    save_data = realtime_collect.realtime_position[
                        ["line_id", "station_id", "train_id", "received_at", "up_down", "last_station_id", "train_status", "express", "is_last_train", "requested_at"]    
                    ].to_dict(orient="records")
                    realtime_cur.executemany(
                        """INSERT INTO realtimes VALUES(
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
                        )""",
                        save_data
                    )
                    realtime_conn.commit()
                    realtime_cur.close()
                    realtime_conn.close()
                    logger.info(f"Success to insert to db. The rows of data is {len(save_data)}")
                except Exception:
                    logger.error(traceback.format_exc())
                # TODO: After the listener is connected, interrupt time.sleep
                time.sleep(self.interval)
            else:
                # Backup data to another db
                prev_realtime_conn = sqlite3.connect(PREV_REALTIME_SAVE_DB_PATH)
                prev_realtime_cur = prev_realtime_conn.cursor()
                
                realtime_conn = sqlite3.connect(REALTIME_SAVE_DB_PATH)
                realtime_cur = realtime_conn.cursor()
                response = realtime_cur.execute("SELECT * FROM realtimes")
                
                arraysize = 100000
                total_rows = 0
                while True:
                    data = response.fetchmany(arraysize)
                    total_rows += len(data)
                    if len(data) == 0: break
                    prev_realtime_cur.executemany(
                        f"INSERT INTO prev_realtimes VALUES ({",".join(["?"]*10)})", data)
                prev_realtime_conn.commit()
                prev_realtime_cur.close()
                prev_realtime_conn.close()
                logger.debug(f"Save realtime db to prev_realtime db. Total rows of data: {total_rows}")
                
                realtime_cur.execute("DELETE FROM realtimes")
                realtime_conn.commit()
                realtime_cur.close()
                realtime_conn.close()
                logger.debug("Delete realtimes data")
                
                # Terminate loop.
                cur_datetime = datetime.now()
                next_start_datetime_str = cur_datetime.date().strftime("%Y-%m-%d") + " 04:50:00" 
                next_start_datetime = datetime.strptime(next_start_datetime_str, "%Y-%m-%d %H:%M:%S")
                next_start_interval = (next_start_datetime - cur_datetime).seconds + 1 # Adding 1 seconds to adjust interval time.
                logger.info(f"Current time: {cur_datetime.strftime("%Y-%m-%d %H:%M:%S")} Loop is terminated. After {next_start_interval//3600}h {next_start_interval%3600//60}m {next_start_interval%3600%60}s, loop will be restarted.")
                
                # Time Sleep
                time.sleep(next_start_interval)
                logger.info(f"Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. Loop is to be started.")
        
    def start(self):
        """ Running on a new thread
        """
        self.t = threading.Thread(target = self.interval_work)
        logger.info(f"Start interval work {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        self.t.start()
        
if __name__ == "__main__":
    logging.basicConfig(
        format = '{asctime}.{msecs:03.0f} {levelname:<8}:{name:<20}:{message}', 
        style =  "{",
        datefmt = "%Y-%m-%d %H:%M:%S",
        level = logging.INFO
    )

    interval = 10
    interval_worker = IntervalCollectWorker(interval = interval)
    interval_worker.start()