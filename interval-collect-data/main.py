import logging
import logging.config
import os
import subprocess
import time

from packages.config import INTERVAL
from packages.interval_collect_worker import IntervalCollectWorker

if __name__ == "__main__":
    if not os.path.exists('log'):
        os.mkdir('log')
        
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
            # "sysout":{
            #     "formatter": "default",
            #     "class": logging.StreamHandler,
            #     "stream": "ext://sys.stdout"
            # },
            "file": {
                "formatter": "default",
                "class": logging.FileHandler,
                "filename": 'log/interval-collect-data.log',
            }
        },
        "loggers": {
            "realtime-collect": {
                "level": "INFO",
                "handlers": ["file"],
                "propagate": False
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["file"]
        }
        
    }
    
    logging.config.dictConfig(config)
    
    # Check commit
    result = subprocess.run("git status -s".split(), capture_output = True)
    if len(result.stdout.decode()) > 0: 
        raise Exception(f"There are not committed Files\n{result.stdout.decode()}")
    
    # Logging version
    result = subprocess.run("git log -n 1".split(), capture_output = True)
    result_parse = result.stdout.decode().split("\n")
    version = result_parse[0].split()[1] # git hash
    commit_date = result_parse[2]
    
    logging.info(
        f"""
        Start interval collect work... PID: {os.getpid()}
        Version: {f"{version}\n{commit_date}"}
        """)
    interval_collect_worker = IntervalCollectWorker(INTERVAL)
    interval_collect_worker.start()
    
    while True:    
        if not interval_collect_worker.check_thread_is_alive():
            logging.error("Interval Collect worker thread is not alive.")
            break
        time.sleep(1)