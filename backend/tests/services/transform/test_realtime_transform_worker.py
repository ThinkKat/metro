from communication.ipc_listener import IPCListener
from communication.ipc_client import IPCClient

from services.transform.src.realtime_transform_worker import RealtimeTransformWorker
from repositories.timetable_repository.postgresql_timetable_repository import PostgresqlTimetableRepository
from repositories.delay_repository.postgresql_delay_repository import PostgresqlDelayRepository
from repositories.realtimes_repository.sqlite_realtime_repository import SqliteRealtimeRepository

import os
from dotenv import load_dotenv

if __name__ == "__main__":
    
    load_dotenv()
    tc_address = os.getenv("TRANSFORM_CONTROLLER_ADDRESS")
    ct_address = os.getenv("COLLECT_TRANSFORM_ADDRESS")
    
    metro_db_url = os.getenv("POSTGRESQL_METRO_DB_URL")
    realtime_db_url = os.getenv("SQLITE_REALTIME_DB_URL")
    
    ipc_listener = IPCListener(tc_address)
    ipc_client = IPCClient(ct_address)
    
    postgresql_timetable_repository = PostgresqlTimetableRepository()
    postgresql_delay_repository = PostgresqlDelayRepository()
    sqlite_realtime_repository = SqliteRealtimeRepository()
    
    ipc_listener.start()
    
    postgresql_timetable_repository.create_engine(metro_db_url)
    postgresql_delay_repository.create_engine(metro_db_url)
    sqlite_realtime_repository.create_engine(realtime_db_url)
    
    realtime_transform_worker = RealtimeTransformWorker(
        ipc_listener,
        ipc_client,
        postgresql_timetable_repository, 
        postgresql_delay_repository, 
        sqlite_realtime_repository
    )
    realtime_transform_worker.start()