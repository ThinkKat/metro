import io

from sqlalchemy import create_engine, text, insert
from sqlalchemy.orm import Session

from model.sqlalchemy_model import Delay

from repositories.delay_repository.delay_repository import DelayRepository

class PostgresqlDelayRepository(DelayRepository):
    
    def create_engine(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        
    def dispose(self):
        self.engine.dispose()
        
    def insert_delay_all(self, data: list[dict]):
        with Session(self.engine) as session:
            insert_stmt = insert(Delay).values(data)
            session.execute(insert_stmt)
            session.commit()
            
    def insert_delay_many(self, data: list[dict], data_size: int = 1000):
        with Session(self.engine) as session:
            for i in range(0, len(data), data_size):
                batch = data[i:i + data_size]
                insert_stmt = insert(Delay).values(batch)
                session.execute(insert_stmt)
            session.commit()
    
    def find_delay_many_by_op_date(self, op_date: str, size: int = 1000) -> dict:
        with Session(self.engine) as session:
            select_stmt = text(
                """
                SELECT *
                FROM delay
                WHERE op_date = :op_date
                """
            )
            response = session.execute(
                select_stmt, 
                {"op_date": op_date}
            )
            columns = response.keys()
            data = []
            row = response.fetchmany(size)
            while len(row) > 0:
                data.extend([{c:r[i] for i, c in enumerate(columns)} for r in row])
                row = response.fetchmany(size)
        return data
            
if __name__ == "__main__":
    """
        Temporary code for finding delay data
    """
    import time
    import pandas as pd

    psql_delay_repository = PostgresqlDelayRepository()
    psql_delay_repository.create_engine("postgresql:///metro")
    
    start_date = "2025-05-01"
    end_date = "2025-05-05"
    
    date = pd.date_range(start_date, end_date)
    df_list = []
    for d in date:
        dt_str = d.date()
        start = time.time()
        data = psql_delay_repository.find_delay_many_by_op_date(dt_str, 1000)
        print(f"{dt_str} {time.time() - start:.5f}초.....")
        df = pd.DataFrame(data)
        df_list.append(df)
    
    total_df = pd.concat(df_list)
    
    total_df.to_csv(f"delay_{start_date}_{end_date}.csv", index = False)
            
