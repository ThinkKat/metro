import threading
import time
import logging
import traceback
from datetime import datetime

import pandas as pd

# Repositories
from repositories.timetable_repository.timetable_repository import TimetableRepository
from repositories.delay_repository.delay_repository import DelayRepository
from repositories.realtimes_repository.realtime_repository import RealtimeRepository

# Transform Module
from services.transform.src.realtime_transform import RealtimeTransform

logger = logging.getLogger('realtime_transform_worker')

class RealtimeTransformWorker:
    def __init__(self,
                 listener,
                 client, 
                 timetable_repoitory: TimetableRepository,
                 delay_repository: DelayRepository, 
                 realtime_repository: RealtimeRepository):
        
        self.delay_repository = delay_repository
        self.realtime_repository = realtime_repository
        
        self.listener = listener
        self.client = client
        self.realtime_transform = RealtimeTransform(timetable_repoitory)
        self.t = None
        
    def interval_work(self):
        # Connect to listener
        self.client.connect()
        while True:
            try:                            
                try:
                    data = self.client.recv()
                    position_data = data["position"]
                    realtime_arrival_all = data["arrival_all"]
                    
                    # position_data == 0 means that the collect loop is stalled. 
                    if isinstance(position_data, int) and position_data == 0:
                        logger.info("Loop is terminated")
                        # Get all realtime data
                        data = self.realtime_repository.find_realtimes(self.realtime_transform.op_d_str)
                        df = pd.DataFrame(data)

                        # Caculate delay time
                        delay_data = self.realtime_transform.get_delay_data(df)
                        delay_data["op_date"] = self.realtime_transform.op_d_str
                        delay_data["day_code"] = self.realtime_transform.day_code
                        delay_data = delay_data.astype({"first_last": "Int16", "stop_no": "Int16"})
                        delay_data["stop_no"] = delay_data["stop_no"].fillna(-1)
                        delay_data["delayed_time"] = delay_data["delayed_time"].dt.total_seconds()
                        
                        logger.info("Start to insert delay data")
                        # Insert delay data
                        usecols = ["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at", "day_code", "first_last", "stop_no", "delayed_time", "op_date"]
                        delay_data = delay_data[usecols].to_dict(orient="records")
                        self.delay_repository.insert_delay_many(delay_data, 10000)
                        logger.info("Success to insert delay data")
                        
                        # Delete realtimes
                        self.realtime_repository.remove_realtimes()
                        continue
                    
                    # position_data == 1 means that the collect loop is started. 
                    elif isinstance(position_data, int) and position_data == 1:
                        logger.info("Loop is started")
                        self.realtime_transform.init()
                        continue
                    
                    else:
                        # Process data
                        self.realtime_transform.process_realtime_data(position_data, realtime_arrival_all)
                        self.listener.set_data(
                            {
                                "position": self.realtime_transform.realtime_position,
                                "arrival": self.realtime_transform.arrival_hashmap
                            }
                        )
                except Exception:
                    logger.info("Client is not connected. Try to connect to listener...")
                    logger.error(traceback.format_exc())
                    self.client.connect()
                    
                    # IF client isn't connected, initialize data
                    if self.client is None:
                        logger.info("Failed to connect. Reset data.")
                        # Reset data
                        self.realtime_transform.init_data()
                    
            except Exception:
                logger.error(traceback.format_exc())
    
    def check_is_alive(self):
        return self.t is not None and self.t.is_alive()
    
    def start(self):
        """ Running on a new thread
        """
        self.t = threading.Thread(target = self.interval_work)
        logger.info(f"Start process work {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        self.t.start()


