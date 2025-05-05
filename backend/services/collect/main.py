import os
import logging
import logging.config
import subprocess
import time

from dotenv import load_dotenv

from communication.ipc_listener import IPCListener 

from services.collect.src.realtime_collect_worker import RealtimeCollectWorker
from repositories.realtimes_repository.sqlite_realtime_repository import SqliteRealtimeRepository

if __name__ == "__main__":
    load_dotenv()
    log_dir = os.getenv("COLLECT_LOG_DIR")
    
    config = {
        "version": 1,
        # disable_existing_loggers: False
        "formatters": {
            "default": {
                "format": '{asctime}.{msecs:03.0f} {levelname:<8}:{name:<25}:{message}',
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "style": "{"
            }
        },
        "handlers":{
            "file": {
                "formatter": "default",
                "class": logging.FileHandler,
                "filename": f'{log_dir}/realtime-collect-process.log',
            }
        },
        "loggers": {
            "realtime_collect_worker": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            },
            "realtime_collect": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            },
            "ipc_listener": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": False
        }
        
    }
    logging.config.dictConfig(config)
    
    """
        Check Commit
        Only after commiting all files in metro projects, it is possible to execute process.
        
        Commit check -> Not committed -> Raise exception
                     -> All committed -> Execute process
                     
        Before executing process, logging git version using hash and date
    """
    # result = subprocess.run("git status -s".split(), capture_output = True)
    # if len(result.stdout.decode()) > 0: 
    #     raise Exception(f"There are not committed Files\nCurrent directory:{os.getcwd()}\n{result.stdout.decode()}")
    
    # # Get git hash and commit date from "git log -n 1" command
    # result = subprocess.run("git log -n 1".split(), capture_output = True)
    # result_parse = result.stdout.decode().split("\n")
    # version = result_parse[0].split()[1] # git hash
    # commit_date = result_parse[2] # commit date
    
    # # Start process
    # logging.info(
    #     f"""
    #     Start realtime collect worker... PID: {os.getpid()}
    #     Version: {f"{version}"}
    #     Commit date: {commit_date}
    #     """)
    
    
    db_url = os.getenv("SQLITE_REALTIME_DB_URL")
    address = os.getenv("COLLECT_TRANSFORM_ADDRESS")
    
    # Parameter
    interval = 10
    # Create IPC listener
    ipc_listener = IPCListener(address)
    ipc_listener.start()
    # Create SQLite repository
    sqlite_realtime_repository = SqliteRealtimeRepository()
    sqlite_realtime_repository.create_engine(db_url)
    
    realtime_collect_worker = RealtimeCollectWorker(
        interval, 
        ipc_listener, 
        sqlite_realtime_repository,
        os.getenv("START_TIME"),
        os.getenv("END_TIME")
    )
    realtime_collect_worker.start()