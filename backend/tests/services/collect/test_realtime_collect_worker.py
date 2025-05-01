from services.collect.src.realtime_collect_worker import RealtimeCollectWorker
from repositories.realtimes_repository.sqlite_realtime_repository import SqliteRealtimeRepository

import os
from dotenv import load_dotenv

if __name__ == "__main__":
    
    load_dotenv()
    db_url = os.getenv("SQLITE_REALTIME_DB_URL")
    address = os.getenv("UDS_ADDRESS")
    
    interval = 10
    sqlite_realtime_repository = SqliteRealtimeRepository()
    sqlite_realtime_repository.create_engine(db_url)
    
    realtime_collect_worker = RealtimeCollectWorker(address, interval, sqlite_realtime_repository)
    realtime_collect_worker.start()