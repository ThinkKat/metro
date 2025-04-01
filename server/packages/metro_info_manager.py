from sqlalchemy import create_engine, select, text, insert, delete
from sqlalchemy.orm import Session

from .sqlalchemy_model import Base, MockRealtime, Delay
from .config import POSTGRESQL_METRO_DB_URL
from .data_model import StationSearchbarList

class MetroInfoManager():
    def __init__(self,):
        self.db_url = f"postgresql://{POSTGRESQL_METRO_DB_URL}"
        self.engine = create_engine(self.db_url)
    
    def get_stations_searchbar(self) -> list[StationSearchbarList]:
        """Get all searchbar station

        Returns:
            dict: station searchbar information
        """
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
            station_searchbar = [{c:StationSearchbarList(**row[i]) for i, c in enumerate(columns)} for row in response.fetchall()]
        return station_searchbar
    
    def get_station_info(self, station_public_code: str) -> dict:
        """Query station information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            dict: station information
        """
        with Session(self.engine) as session:
            response = session.execute(text(
                    "SELECT * FROM stations WHERE station_public_code = :station_public_code"
                ),
                {"station_public_code": station_public_code}
            )
            columns = response.keys()
            row = response.fetchone()
        
        # If there not exists station information
        if row is not None:
            station_info = {c:row[i] for i, c in enumerate(columns)}
            if station_info["left_direction"] == 0:
                station_info["up"] = "left_direction"
                station_info["down"] = "right_direction"
            else:
                station_info["up"] = "right_direction"
                station_info["down"] = "left_direction"
            return station_info
        else:
            return {
                "error": "Wrong station public code. There exists no station information.",
                "station_public_code": station_public_code
            }
        
    def get_line_info(self, line_id: int) -> dict:
        """Query line information

        Args:
            line_id (int): an unique line id

        Returns:
            dict: line information
        """
        with Session(self.engine) as session:
            response = session.execute(text(
                    "SELECT * FROM lines WHERE line_id = :line_id",
                ),
                {"line_id": line_id}
            )
            columns = response.keys()
            row = response.fetchone()
            line_info = {c:row[i] for i, c in enumerate(columns)}
        return line_info
    
    def get_adjacent_stations(self, station_public_code: str) -> list[dict]:
        """Query connections information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: adjacent station information
        """
        with Session(self.engine) as session:
            response = session.execute(text(
                    "SELECT * FROM connections WHERE from_station_public_code = :station_public_code",
                ),
                {"station_public_code": station_public_code}
            )
            columns = response.keys()
            rows = response.fetchall()
            connections = [{c:row[i] for i, c in enumerate(columns)} for row in rows]
        return connections
        
    def get_transfer_lines(self, line_id: int, station_public_code: str) -> list[dict]:
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
                    SELECT *
                    FROM transfers
                    WHERE transfer_station_code = (
                        SELECT transfer_station_code 
                        FROM transfers 
                        WHERE station_public_code = :station_public_code
                    )
                    AND line_id <> :line_id
                    """
                ),
                {"station_public_code": station_public_code, "line_id": line_id}
            )
            columns = response.keys()
            rows = response.fetchall()
            transfer_info = [{c:row[i] for i, c in enumerate(columns)} for row in rows]
        
        return transfer_info
    
    def get_timetable(self, op_date: str, station_public_code: str) -> list[dict]:
        """Query timetable information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: timetable information
        """
        with Session(self.engine) as session:
            response = session.execute(text(
                    """
                    SELECT *
                    FROM timetables
                    WHERE ((updated_at <= :op_date AND end_date > :op_date) OR (end_date IS NULL))
                    AND station_public_code = :station_public_code
                    """
                ),
                {"op_date": op_date, "station_public_code": station_public_code}
            )
            columns = response.keys()
            rows = response.fetchall()
            timetable_info = [{c:row[i] for i, c in enumerate(columns)} for row in rows]
        
        return timetable_info
    
if __name__ == "__main__":
    metro_info_manager = MetroInfoManager()
    import time
    start = time.time()
    station_public_code = "123" # 회기역
    day_code = 8
    print(metro_info_manager.get_timetable("2025-03-30", station_public_code))