from sqlalchemy import create_engine, select, text, insert, delete
from sqlalchemy.orm import Session

from repositories.delay_repository.delay_repository import DelayRepository

class PostgresqlDelayRepository(DelayRepository):
    
    def create_engine(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        
    def dispose(self):
        self.engine.dispose()
        
    def insert_delay(self, data: list[dict]):
        with Session(self.engine) as session:
            insert_stmt = insert(Delay).values(data)
            session.execute(upsert_stmt)
            session.commit()
            
            