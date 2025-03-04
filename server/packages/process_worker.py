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
        self.run_loop = self.check_time()
        self.realtime_process = RealtimeProcess()
    
    def check_time(self):
        # Maintaining time: 04:50 - 01:30 (tomorrow)
        dt_str_now = datetime.now().strftime("%H:%M:%S")
        return dt_str_now >= "04:50:00" or dt_str_now <= "01:30:00"
    
    def interval_work(self):
        while True:
            try:
                self.run_loop = self.check_time()
                
                # Re-init when
                if not self.run_loop:
                    self.realtime_process.init()
                    
                    # # Sleep process to 04:50
                    # cur_datetime = datetime.now()
                    # next_start_datetime_str = cur_datetime.date().strftime("%Y-%m-%d") + " 04:50:00" 
                    # next_start_datetime = datetime.strptime(next_start_datetime_str, "%Y-%m-%d %H:%M:%S")
                    # next_start_interval = (next_start_datetime - cur_datetime).seconds + 1 # Adding 1 seconds to adjust interval time.
                    # logger.info(f"Current time: {cur_datetime.strftime("%Y-%m-%d %H:%M:%S")}. After {next_start_interval//3600}h {next_start_interval%3600//60}m {next_start_interval%3600%60}s, process will be restarted.")
                    
                    # # Time Sleep
                    # time.sleep(next_start_interval)
                    # logger.info(f"Current time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. Process is to be started.")
                
                # When the client is connected to listeners
                try:
                    position_data = self.realtime_process.client.recv()
                    realtime_arrival_all = self.realtime_process.client.recv()
                    
                    # Process data
                    self.realtime_process.process_realtime_data(position_data, realtime_arrival_all)
                except Exception:
                    logger.info("Client is not connected. Try to connect to listener...")
                    self.realtime_process.connect()
                    
                    # IF client isn't connected, initialize data
                    if self.realtime_process.client is None:
                        logger.info("Failed to connect. Reset data.")
                        # Reset data
                        self.realtime_process.init_data()
                    
            except Exception:
                import traceback
                print(traceback.format_exc())
    
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