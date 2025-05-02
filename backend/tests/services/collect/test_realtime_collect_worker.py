from communication.ipc_listener import IPCListener 

from services.collect.src.realtime_collect_worker import RealtimeCollectWorker
from repositories.realtimes_repository.sqlite_realtime_repository import SqliteRealtimeRepository

import os
from dotenv import load_dotenv

if __name__ == "__main__":
    
    load_dotenv()
    db_url = os.getenv("SQLITE_REALTIME_DB_URL")
    address = os.getenv("COLLECT_TRANSFORM_ADDRESS")
    
    # Parameter
    interval = 10
    ipc_listener = IPCListener(address)
    ipc_listener.start()
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