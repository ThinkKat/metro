import os
from dotenv import load_dotenv

from communication.ipc_listener import IPCListener
from communication.ipc_client import IPCClient

from services.transform.src.realtime_transform_worker import RealtimeTransformWorker
from repositories.timetable_repository.postgresql_timetable_repository import PostgresqlTimetableRepository
from repositories.delay_repository.postgresql_delay_repository import PostgresqlDelayRepository
from repositories.realtimes_repository.sqlite_realtime_repository import SqliteRealtimeRepository

from model.pydantic_model import RealtimePosition, RealtimeArrival

load_dotenv()
tc_address = os.getenv("TRANSFORM_CONTROLLER_ADDRESS")
ct_address = os.getenv("COLLECT_TRANSFORM_ADDRESS")

metro_db_url = os.getenv("POSTGRESQL_METRO_DB_URL")
realtime_db_url = os.getenv("SQLITE_REALTIME_DB_URL")

arrival_line = list(map(int, os.getenv("ARRIVAL_LINE").split(",")))

ipc_listener = IPCListener(tc_address)
ipc_client = IPCClient(ct_address)

postgresql_timetable_repository = PostgresqlTimetableRepository()
postgresql_delay_repository = PostgresqlDelayRepository()
sqlite_realtime_repository = SqliteRealtimeRepository()

# ipc_listener.start() # Not using

postgresql_timetable_repository.create_engine(metro_db_url)
postgresql_delay_repository.create_engine(metro_db_url)
sqlite_realtime_repository.create_engine(realtime_db_url)

realtime_transform_worker = RealtimeTransformWorker(
    ipc_listener,
    ipc_client,
    postgresql_timetable_repository, 
    postgresql_delay_repository, 
    sqlite_realtime_repository,
    arrival_line
)
realtime_transform_worker.start()

def get_position_by_line_id(line_id: int) -> RealtimePosition:
    position = realtime_transform_worker.realtime_transform.realtime_position
    if line_id in position:
        return position[line_id]
    else:
        return RealtimePosition(**{"place": []})
    

def get_arrival_by_station_id(station_id: int, up: str, down: str) -> RealtimeArrival:
        """Get arrival data by station_id 

        Args:
            station_id (int): _description_
            up (str): _description_
            down (str): _description_

        Returns:
            RealtimeArrival: _description_
        """
        
        # Create arrival data
        data = {"left": [], "right": []}
        
        arrival = realtime_transform_worker.realtime_transform.arrival_hashmap
        # Get data by id
        if station_id in arrival:
            realtime_arrival = arrival[station_id]
        else:
            realtime_arrival = []
        
        # up: "left_direction", down: "right_direction"
        for row in realtime_arrival:
            if row.up_down == 0:
                data[up.split("_")[0]].append(row)
            else:
                data[down.split("_")[0]].append(row)
        return RealtimeArrival(**data)

