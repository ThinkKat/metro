from sqlalchemy import create_engine, select, text, insert, delete
from sqlalchemy.orm import Session

from repositories.timetable_repository.timetable_repository import TimetableRepository
from model.pydantic_model import Timetable, TimetableRow

class PostgresqlTimetableRepository(TimetableRepository):
    
    def create_engine(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        
    def dispose(self):
        self.engine.dispose()
        
    def find_timetable_for_calculation_delay(self, op_date: str, day_code: int) -> list:
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT 
                        tb.line_id,
                        tb.first_station_name,
                        tb.last_station_name,
                        tb.first_last,
                        tb.station_public_code,
                        tb.day_code,
                        tb.up_down,
                        tb.express,
                        tb.arrival_time,
                        tb.department_time,
                        tb.realtime_train_id,
                        tb.stop_no,
                        tb.express_non_stop,
                        s.station_id,
                        s.station_name
                    FROM timetables tb
                    INNER JOIN stations s
                    ON tb.line_id = s.line_id
                    AND tb.station_public_code = s.station_public_code
                    WHERE (tb.updated_at <= :op_date AND (tb.end_date > :op_date OR tb.end_date IS NULL))
                    AND tb.day_code = :day_code
                    """),
                {"op_date":op_date, "day_code": day_code}
            )
            columns = response.keys()
            data = [
                {c:row[i] for i, c in enumerate(columns)} 
                for row in response.fetchall()
            ]
        return data
        
    def find_timetable_by_station_public_code(self, op_date: str, station_public_code: str) -> list:
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT 
                        *,
                        CASE
                            WHEN hour < 5 THEN hour + 24
                            ELSE hour
                        END AS sort_hour_key,
                        minute AS sort_minute_key,
                        CASE
                            WHEN CAST(stb.up_down AS INT) = s.left_direction THEN 'left'
                            ELSE 'right'
                        END AS direction
                    FROM (
                        SELECT 
                            *,
                            CAST(EXTRACT(HOUR FROM t.department_time) AS INT) AS hour,
                            CAST(EXTRACT(MINUTE FROM t.department_time) AS INT) AS minute
                        FROM timetables t
                        WHERE t.station_public_code = :station_public_code
                        AND (t.updated_at <= :op_date AND (t.end_date > :op_date OR t.end_date IS NULL))
                    ) stb
                    LEFT JOIN stations s
                    ON stb.station_public_code = s.station_public_code
                    ORDER BY sort_hour_key, sort_minute_key
                    """),
                {"op_date":op_date ,"station_public_code": station_public_code}
            )
            columns = response.keys()
            data = [
                {c:row[i] for i, c in enumerate(columns)} 
                for row in response.fetchall()
            ]
            timetable = {"left": [], "right": []}
            for row in data:
                timetable[row["direction"]].append(TimetableRow(**row))
        return Timetable(**timetable)

if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    import os
    import time
    from sqlalchemy import create_engine

    load_dotenv()
    db_url = os.getenv("POSTGRESQL_METRO_DB_URL")
    
    repository = PostgresqlTimetableRepository()
    repository.create_engine(db_url)
    start_time = time.time()
    
    # Test find_total_station_info
    tb_for_calculation = repository.find_timetable_for_calculation_delay('2025-05-01', 1)
    # print(tb_for_calculation)
    print(f"find_timetable_for_calculation_delay Execution time: {time.time() - start_time} seconds")
    
    start_time = time.time()
    data = repository.find_timetable_by_station_public_code('2025-05-01',"123")
    # print(data)
    print(f"find_timetable_by_station_public_code Execution time: {time.time() - start_time} seconds")
    repository.dispose()