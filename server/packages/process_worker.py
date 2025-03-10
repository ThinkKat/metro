import threading
import time
import logging
import traceback
from datetime import datetime

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
                        continue
                    
                    # position_data == 1 means that the collect loop is started. 
                    if isinstance(position_data, int) and position_data == 1:
                        logger.info("Loop is started")
                        self.realtime_process.init()
                        continue
                    
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