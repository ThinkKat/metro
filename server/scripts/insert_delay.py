import pandas as pd
from sqlalchemy import create_engine, select, text, insert, delete
from sqlalchemy.orm import Session

from packages.sqlalchemy_model import Base, MockRealtime, Delay
from packages.config import SQLITE_REALTIME_DB_PATH, POSTGRESQL_METRO_DB_URL

tmp = pd.read_csv(
    "./total_delay.csv", 
    dtype = {"first_last": "Int16", "train_id": "string"}, 
    chunksize=10000, 
    iterator=True
)

db_url = f"postgresql://{POSTGRESQL_METRO_DB_URL}"
engine = create_engine(db_url)
Base.metadata.create_all(engine)
usecols = ["line_id", "station_id", "train_id", "received_at", "train_status", "requested_at", "day_code", "first_last", "stop_no", "delayed_time", "op_date"]
count = 0
with Session(engine) as session:
    while True:
        try:
            data = next(tmp)
            count += len(data)
            print(count)
        except StopIteration:
            print("Done!")
            break
        delay_data = data[usecols].to_dict(orient="records")
        
        insert_stmt = insert(Delay).values(delay_data)
        session.execute(insert_stmt)
        session.commit()