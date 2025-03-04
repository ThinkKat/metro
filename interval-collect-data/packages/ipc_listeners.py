import logging
import time
import traceback
import threading
from multiprocessing.connection import Listener

logger = logging.getLogger("realtime-collect")

class IPCListner:
    def __init__(self, address: tuple[str, int] = ('localhost', 6000)):
        self.listener = Listener(address)
        self.data: list = {}
        self.update = False # Sending data only once.
        self.conn = None
    
    def open_pipe(self):
        logger.info("Open listener...")
        self.conn = None
        self.conn = self.listener.accept() # Wait till connecting to client  
        logger.info("Connected to client")
    
    def set_data(self, data: list):
        self.data = data
        self.update = True
        if self.conn is None: logger.debug("Not yet connected...")
    
    def start(self):
        """
            Listener Connection for IPC.
            Check the pipe connection continuously every second.
            IF the pipe is broken, reopen pipe connection.
            
            Check pipe connection logic:
            
                if self.conn.poll(): -> True when either the pipe is broken or the data is sent to client. 
                                        There are never the case that a client sends data. 
                                        So, if this is True, the pipe must be broken, exclusively.
                    self.conn.recv() -> Raise BrokenPipeError
        """
        
        self.open_pipe()
        
        # Send data
        while True:
            try:
                if self.update:
                    logger.debug("Send data...")
                    for d in self.data:
                        self.conn.send(d)
                    self.update = False
                
                # Check pipe break
                if self.conn.poll():
                    self.conn.recv()
            except Exception:
                logger.error(traceback.format_exc())
                self.open_pipe()
            time.sleep(0.5)
    
    
        
            
        
            
            