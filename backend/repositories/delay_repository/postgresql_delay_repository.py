from sqlalchemy import create_engine, insert, Delay
from sqlalchemy.orm import Session

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
            
            