
from sqlalchemy import create_engine, select, text, insert, delete
from sqlalchemy.orm import Session

from repositories.metro_repository.metro_repository import MetroRepository
from model.pydantic_model import StationSearchbarList, StationInfo, Station, Line, TransferLine, AdjacentStation

class PostgresqlMetroRepository(MetroRepository):
    
    def create_engine(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        
    def dispose(self):
        self.engine.dispose()
        
    def find_stations_searchbar(self) -> list[StationSearchbarList]:
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT 
                        l.line_id AS line_id,
                        l.line_color AS line_color,
                        l.line_name AS line_name,
                        s.station_public_code AS station_public_code,
                        s.station_name AS station_name
                    FROM stations s
                    INNER JOIN lines l
                    ON s.line_id = l.line_id
                    """
                )
            )
            columns = response.keys()
            data = response.fetchall()
        return [
            StationSearchbarList(**{c:row[i] for i, c in enumerate(columns)}) 
            for row in data
        ]
    
    def find_total_station_info(self, station_public_code: str) -> StationInfo:
        '''
            Return station information
                1. station
                2. line_info
                    1. line_id
                    2. line_name
                    3. line_color
                3. transfer_lines
                4. adjacent_stations
        '''
        station = self.find_station(station_public_code)
        line = self.find_line(station["line_id"])
        transfer_lines = self.find_transfer_lines(station_public_code)
        adjacent_stations = {"left":[], "right":[]}
        for adj in self.find_adjacent_stations(station_public_code):
            adjacent_stations[adj["direction"]].append(AdjacentStation(**adj))
            
        data = {
            "station": Station(**station),
            "line": Line(**line),
            "transfer_lines": [TransferLine(**t) for t in transfer_lines],
            "adjacent_stations": adjacent_stations
        }
        return StationInfo(**data)
    
    def find_station(self, station_public_code: str) -> dict:
        '''
            Return station information
        '''
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT 
                        station_public_code,
                        station_id,
                        station_name,
                        request_station_name,
                        left_direction,
                        right_direction,
                        CASE
                            WHEN left_direction = 0 THEN 'left'
                            ELSE 'right'
                        END AS up,
                        CASE
                            WHEN left_direction = 1 THEN 'left'
                            ELSE 'right'
                        END AS down,
                        line_id
                    FROM stations
                    WHERE station_public_code = :station_public_code
                    """,
                ),
                {"station_public_code": station_public_code}
            )
            columns = response.keys()
            row = response.fetchone()
            data = {c:row[i] for i, c in enumerate(columns)}
        return data
        
        
    def find_line(self, line_id: int) -> dict:
        """Query line information

        Args:
            line_id (int): an unique line id

        Returns:
            dict: line information
        """
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT * FROM lines WHERE line_id = :line_id
                    """,
                ),
                {"line_id": line_id}
            )
            columns = response.keys()
            row = response.fetchone()
            data = {c:row[i] for i, c in enumerate(columns)}
        return data
    
    def find_adjacent_stations(self, station_public_code: str) -> list[dict]:
        """Query connections information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: adjacent station information
        """
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT 
                        s.station_public_code,
                        s.station_id,
                        s.station_name,
                        s.request_station_name,
                        s.left_direction,
                        s.right_direction,
                        CASE
                            WHEN left_direction = 0 THEN 'left'
                            ELSE 'right'
                        END AS up,
                        CASE
                            WHEN left_direction = 1 THEN 'left'
                            ELSE 'right'
                        END AS down,
                        CASE
                            WHEN adj.up_down THEN 1
                            ELSE 0
                        END as up_down,
                        adj.direction
                    FROM (
                        SELECT * 
                        FROM connections 
                        WHERE from_station_public_code = :station_public_code
                    ) adj
                    LEFT JOIN stations s
                    ON adj.to_station_public_code = s.station_public_code
                    """,
                ),
                {"station_public_code": station_public_code}
            )
            columns = response.keys()
            rows = response.fetchall()
            data = [
                {c:row[i] for i, c in enumerate(columns)} 
                for row in rows
            ]
        return data
    
    def find_transfer_lines(self, station_public_code: str) -> list[dict]:
        """ Query transfer lines.
            Information about same stations of other lines.
            
        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: adjacent station information
            adjacent_station = {
                
            }
        """
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT 
                        l.line_id,
                        l.line_name,
                        l.line_color,
                        t.station_public_code
                    FROM (
                        SELECT *
                        FROM transfers
                        WHERE transfer_station_code = (
                            SELECT transfer_station_code 
                            FROM transfers 
                            WHERE station_public_code = :station_public_code
                        )
                    ) t
                    LEFT JOIN lines l
                    ON t.line_id = l.line_id
                    """
                ),
                {"station_public_code": station_public_code}
            )
            columns = response.keys()
            rows = response.fetchall()
            data = [{c:row[i] for i, c in enumerate(columns)} for row in rows]
        
        return data
    
    
if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    import os
    import time
    from sqlalchemy import create_engine

    load_dotenv()
    db_url = os.getenv("POSTGRESQL_METRO_DB_URL")
    
    repository = PostgresqlMetroRepository()
    repository.create_engine(db_url)
    start_time = time.time()
    
    # Test find_total_station_info
    data = repository.find_total_station_info("123")
    print(data)
    print(f"Execution time: {time.time() - start_time} seconds")
    repository.dispose()