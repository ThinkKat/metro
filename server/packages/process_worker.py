import threading
import time
import logging
import traceback
from datetime import datetime

import pandas as pd
from sqlalchemy import create_engine, text, insert
from sqlalchemy.orm import sessionmaker

from .config import SQLITE_REALTIME_DB_PATH, SQLITE_TEST_REALTIME_DB_PATH, POSTGRESQL_METRO_DB_URL
from .sqlalchemy_model import Delay
from .realtime_process import RealtimeProcess

logger = logging.getLogger("process-worker")

class ProcessWorker:
    def __init__(self):
        self.t = None
        self.realtime_process = RealtimeProcess()
    
    def interval_work(self):
        while True:
            try:            
                # When the client is connected to listeners
                try:
                    position_data = self.realtime_process.client.recv()
                    realtime_arrival_all = self.realtime_process.client.recv()
                    
                    # position_data == 0 means that the collect loop is stalled. 
                    if isinstance(position_data, int) and position_data == 0:
                        logger.info("Loop is terminated")
                        # Get all realtime data
                        sqlite_session = sessionmaker(bind = create_engine(f"sqlite://{SQLITE_REALTIME_DB_PATH}"))()
                        select_stmt = text("SELECT * FROM realtimes")
                        response = sqlite_session.execute(select_stmt)
                        df = pd.DataFrame(response.fetchall(), columns = response.keys())

                        # Caculate delay time
                        delay_data = self.realtime_process.get_delay_data(df)
                        delay_data["op_date"] = self.realtime_process.op_d_str
                        delay_data["day_code"] = self.realtime_process.day_code
                        delay_data = delay_data.astype({"first_last": "Int16", "stop_no": "Int16"})
                        delay_data["stop_no"] = delay_data["stop_no"].fillna(-1)
                        delay_data["delayed_time"] = delay_data["delayed_time"].dt.total_seconds()
                        
                        # Insert delay data
                        postgresql_session = sessionmaker(bind = create_engine(f"postgresql://{POSTGRESQL_METRO_DB_URL}"))()
                        usecols = ["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at", "day_code", "first_last", "stop_no", "delayed_time", "op_date"]
                        delay_data = delay_data[usecols].to_dict(orient="records")
                        for d in delay_data:
                            insert_stmt = insert(Delay).values(d)
                            postgresql_session.execute(insert_stmt)
                        postgresql_session.commit()
                        
                        # Delete realtimes
                        delete_stmt = text("DELETE FROM realtimes")
                        sqlite_session.execute(delete_stmt)
                        sqlite_session.commit()
                        continue
                    
                    # position_data == 1 means that the collect loop is started. 
                    elif isinstance(position_data, int) and position_data == 1:
                        logger.info("Loop is started")
                        self.realtime_process.init()
                        continue
                    
                    else:
                        # Process data
                        self.realtime_process.process_realtime_data(position_data, realtime_arrival_all)
                except Exception:
                    logger.info("Client is not connected. Try to connect to listener...")
                    logger.error(traceback.format_exc())
                    self.realtime_process.connect()
                    
                    # IF client isn't connected, initialize data
                    if self.realtime_process.client is None:
                        logger.info("Failed to connect. Reset data.")
                        # Reset data
                        self.realtime_process.init_data()
                    
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
        
if __name__ == "__main__":
    logging.basicConfig(
        format = '{asctime}.{msecs:03.0f} {levelname:<8}:{name:<20}:{message}', 
        style =  "{",
        datefmt = "%Y-%m-%d %H:%M:%S",
        level = logging.INFO
    )

    process_worker = ProcessWorker()
    process_worker.start()