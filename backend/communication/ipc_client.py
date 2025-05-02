import os
import traceback
import time
import logging

from multiprocessing.connection import Client

logger = logging.getLogger("ipc_client")

class IPCClient:
    def __init__(self, address):
        self.address = address
        self.client = None
            
    def connect(self):
        # Client
        try:
            self.client = Client(self.address)
            logger.info("Connected to listener")
            print("Connected to listener")
        except ConnectionRefusedError:
            # This excpetion is raised when the pipe isn't opening.
            logger.error(traceback.format_exc())
            time.sleep(5)
            self.client = None
        except FileNotFoundError:
            # This exception is raised when the uds(AF_UNIX) files doesn't exists
            logger.error(traceback.format_exc())
            time.sleep(5)
            self.client = None
        except Exception:
            logger.error(traceback.format_exc())
            self.client = None
    
    def recv(self):
        return self.client.recv()
    
    def close(self):
        self.client.close()     
        