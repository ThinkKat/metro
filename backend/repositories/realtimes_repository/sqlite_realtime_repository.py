
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert

from repositories.realtimes_repository.realtime_repository import RealtimeRepository
from model.sqlalchemy_model import Realtime

class SqliteRealtimeRepository(RealtimeRepository):
    
    def create_engine(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        
    def dispose(self):
        self.engine.dispose()
        
    def find_realtimes(self, op_date: str) -> list[dict]:
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT *
                    FROM realtimes
                    WHERE DATE(received_at, "-04:50:00") = :op_date
                    """),
                {"op_date":op_date}
            )
            columns = response.keys()
            data = [
                {c:row[i] for i, c in enumerate(columns)} 
                for row in response.fetchall()
            ]
        return data
    
    def remove_realtimes(self):
        with Session(self.engine) as session:
            delete_stmt = text("DELETE FROM realtimes")
            session.execute(delete_stmt)
            session.commit()
            
    def upsert_realtimes(self, data: list[dict]):
        with Session(self.engine) as session:
            insert_stmt = insert(Realtime).values(data)
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=['line_id', 'station_id', 'train_id', 'train_status'],
                set_={"received_at": insert_stmt.excluded.received_at, "requested_at": insert_stmt.excluded.requested_at}
            )
            session.execute(upsert_stmt)
            session.commit()