import os
import io

import pandas as pd
from sqlalchemy import create_engine, insert, delete, text
from sqlalchemy.orm import Session

from packages.sqlalchemy_model import Base, Regions, Lines, Stations, Transfers, Connections, Timetables
from packages.config import POSTGRESQL_METRO_DB_URL

def init_table(table_model: Base, data: list[dict]):
    """Use insert
    """
    engine = create_engine(f"postgresql://{POSTGRESQL_METRO_DB_URL}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        # Clear table
        session.execute(delete(table_model))
        # Insert table
        session.execute(insert(table_model).values(data))
        session.commit()

def init_table2(table_model: Base, file_pah: str):
    """Use copy
    """
    buffer = io.StringIO(open(file_pah).read())
    engine = create_engine(f"postgresql://{POSTGRESQL_METRO_DB_URL}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        # Clear table
        session.execute(delete(table_model))
        cursor = session.connection().connection.cursor()
        columns = buffer.readline()
        # Insert table
        cursor.copy_expert(
            f"COPY {table_model.__tablename__} ({columns}) FROM STDIN WITH CSV",
            buffer
        )
        session.commit()
        
if __name__ == "__main__":
    table_dict = {
        "regions": Regions,
        "lines": Lines,
        "stations": Stations,
        "transfers": Transfers,
        "connections": Connections,
        "timetables": Timetables
    }
    
    table_dtype = {
        "timetables": {
            "line_id": "int",
            "train_id": "string",
            "first_station_name": "string",
            "last_station_name": "string",
            "first_last": "int",
            "station_public_code": "string",
            "day_code": "int",
            "up_down": "int",
            "express": "int",
            "arrival_time": "string",
            "department_time": "string",
            "updated_at": "string",
            "end_date": "string",
            "realtime_train_id": "string",
            "stop_no": "int",
            "express_non_stop": "int"
        }
    }
    
    for k, v in table_dict.items():
        print(f"Insert data {k}")
        dtype = {}
        if k in table_dtype:
            dtype = table_dtype[k]
        file_path = f"{os.getcwd()}/assets/metro_information/{k}.csv"
        init_table2(v, file_path)
        