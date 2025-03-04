import logging
import logging.config
import os

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
            "sysout":{
                "formatter": "default",
                "class": logging.StreamHandler,
                "stream": "ext://sys.stdout"
            },
            "file": {
                "formatter": "default",
                "class": logging.FileHandler,
                "filename": 'log/interval-collect-data.log',
            }
        },
        "loggers": {
            "realtime-collect": {
                "level": "INFO",
                "handlers": ["sysout", "file"],
                "propagate": False
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["sysout", "file"]
        }
        
    }
    
    logging.config.dictConfig(config)
    
    logging.info(f"Start interval collect work... PID: {os.getpid()}")
    interval_collect_worker = IntervalCollectWorker(INTERVAL)
    interval_collect_worker.start()