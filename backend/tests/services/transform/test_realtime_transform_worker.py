from services.transform.src.realtime_transform_worker import RealtimeTransformWorker
from repositories.timetable_repository.postgresql_timetable_repository import PostgresqlTimetableRepository
from repositories.delay_repository.postgresql_delay_repository import PostgresqlDelayRepository
from repositories.realtimes_repository.sqlite_realtime_repository import SqliteRealtimeRepository

import os
from dotenv import load_dotenv

if __name__ == "__main__":
    
    load_dotenv()
    address = os.getenv("UDS_ADDRESS")
    metro_db_url = os.getenv("POSTGRESQL_METRO_DB_URL")
    realtime_db_url = os.getenv("SQLITE_REALTIME_DB_URL")
    
    postgresql_timetable_repository = PostgresqlTimetableRepository()
    postgresql_delay_repository = PostgresqlDelayRepository()
    sqlite_realtime_repository = SqliteRealtimeRepository()
    
    postgresql_timetable_repository.create_engine(metro_db_url)
    postgresql_delay_repository.create_engine(metro_db_url)
    sqlite_realtime_repository.create_engine(realtime_db_url)
    
    realtime_transform_worker = RealtimeTransformWorker(
        address,    
        postgresql_timetable_repository, 
        postgresql_delay_repository, 
        sqlite_realtime_repository
    )
    realtime_transform_worker.start()