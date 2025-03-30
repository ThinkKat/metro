import threading
import time
import logging
import traceback
import os
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert

from .ipc_listeners import IPCListner
from .config import SQLITE_REALTIME_DB_PATH
from .realtime_collect import RealtimeCollect
from .sqlalchemy_model import Base, MockRealtime, Realtime

logger = logging.getLogger("realtime-collect")

class IntervalCollectWorker:
    def __init__(self, interval: int):
        self.db_url = f"sqlite://{SQLITE_REALTIME_DB_PATH}"
        self.engine = create_engine(self.db_url)

        self.interval = interval
        self.run_loop = self.check_time()
        self.listener = IPCListner()
        self.t = None # Set thread to an attribute.
    
    def check_thread_is_alive(self):
        return self.t is not None and self.t.is_alive()
    
    def check_time(self):
        # Maintaining time: 04:50 - 01:30 (tomorrow)
        dt_str_now = datetime.now().strftime("%H:%M:%S")
        return dt_str_now >= "04:50:00" or dt_str_now <= "00:00:00"
        # return False
    
    def interval_work(self):
        # Open ipc listener
        t = threading.Thread(target = self.listener.start)
        t.start()
                
        # Realtime Collect Module
        realtime_collect = RealtimeCollect()
        Base.metadata.create_all(self.engine)
        
        while True:
            self.run_loop = self.check_time()
            if self.run_loop:
                try:
                    # Process data
                    realtime_collect.collect_realtime_data()
                    
                    # Send data
                    self.listener.set_data([realtime_collect.realtime_position, realtime_collect.realtime_arrival_all])
                    
                    # Save data 
                    with Session(self.engine) as session:
                        data = realtime_collect.realtime_position
                        data["received_at"] = pd.to_datetime(data["received_at"], format="%Y-%m-%d %H:%M:%S")
                        data["requested_at"] = pd.to_datetime(data["requested_at"], format="%Y-%m-%d %H:%M:%S")
                        
                        save_data = data[
                            ["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at"]    
                        ].to_dict(orient="records")
                        insert_stmt = insert(Realtime).values(save_data)
                        upsert_stmt = insert_stmt.on_conflict_do_update(
                            index_elements=['line_id', 'station_id', 'train_id', 'train_status'],
                            set_={"received_at": insert_stmt.excluded.received_at, "requested_at": insert_stmt.excluded.requested_at}
                        )
                        session.execute(upsert_stmt)
                        session.commit()

                    logger.debug(f"Success to insert to db. The rows of data is {len(save_data)}")
                except Exception:
                    logger.error(traceback.format_exc())
                # TODO: After the listener is connected, interrupt time.sleep
                time.sleep(self.interval)
            else:
                # Send the signal to notice that the loop is stalled
                self.listener.set_data([0, 0])
                
                # Terminate loop.
                cur_datetime = datetime.now()
                next_start_datetime_str = cur_datetime.date().strftime("%Y-%m-%d") + " 04:50:00" 
                next_start_datetime = datetime.strptime(next_start_datetime_str, "%Y-%m-%d %H:%M:%S")
                next_start_interval = (next_start_datetime - cur_datetime).seconds + 1 # Adding 1 seconds to adjust interval time.
                logger.info(f"Current time: {cur_datetime.strftime("%Y-%m-%d %H:%M:%S")} Loop is terminated. After {next_start_interval//3600}h {next_start_interval%3600//60}m {next_start_interval%3600%60}s, loop will be restarted.")
                
                # Time Sleep
                time.sleep(next_start_interval)
                logger.info(f"Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. Loop is to be started.")
                
                # Send the signal to notice that the loop is started
                self.listener.set_data([1, 1])
        
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