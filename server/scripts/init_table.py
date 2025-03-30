import pandas as pd
from sqlalchemy import create_engine, insert, delete
from sqlalchemy.orm import Session

from packages.sqlalchemy_model import Base, Regions, Lines, Stations, Transfers, Connections
from packages.config import SQLITE_REALTIME_DB_PATH, POSTGRESQL_METRO_DB_URL

def init_table(table_model: Base, data: list[dict]):
    engine = create_engine(f"postgresql://{POSTGRESQL_METRO_DB_URL}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        # Clear table
        session.execute(delete(table_model))
        # Insert table
        session.execute(insert(table_model).values(data))
        session.commit()
        
if __name__ == "__main__":
    table_dict = {
        "regions": Regions,
        "lines": Lines,
        "stations": Stations,
        "transfers": Transfers,
        "connections": Connections
    }
    
    for k, v in table_dict.items():
        print(f"Insert data {k}")
        data = pd.read_csv(f"./assets/subways_data/{k}.csv").to_dict(orient="records")
        init_table(v, data)