from .config import TIMETABLE_DB_PATH
from .db_manager import DBManager
from .data_model import StationSearchbar

class TimetableDBManager(DBManager):
    def __init__(self, timetable_db_path: str = TIMETABLE_DB_PATH):
        super().__init__(timetable_db_path)    
    
    def get_stations_searchbar(self) -> list[StationSearchbar]:
        """Get all searchbar station

        Returns:
            dict: station searchbar information
        """
        rows = self.execute(
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
        ).fetchall()
        columns = self.get_column_names()
        station_searchbar = [self.dict_factory(row, columns) for row in rows]
        return station_searchbar
    
    def get_station_info(self, station_public_code: str) -> dict:
        """Query station information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            dict: station information
        """
        row = self.execute(
            "SELECT * FROM stations WHERE station_public_code = :station_public_code", 
            {"station_public_code": station_public_code}
        ).fetchone()
        
        # If there not exists station information
        if row is not None:
            columns = self.get_column_names()
            station_info = self.dict_factory(row, columns)
            if station_info["left"] == 0:
                station_info["up"] = "left"
                station_info["down"] = "right"
            else:
                station_info["up"] = "right"
                station_info["down"] = "left"
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
        row = self.execute(
            "SELECT * FROM lines WHERE line_id = :line_id", 
            {"line_id": line_id}
        ).fetchone()
        columns = self.get_column_names()
        line_info = self.dict_factory(row, columns)
        return line_info
    
    def get_adjacent_stations(self, station_public_code: str) -> list[dict]:
        """Query connections information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: adjacent station information
        """
        rows = self.execute(
            "SELECT * FROM connections WHERE from_station_public_code = :station_public_code", 
            {"station_public_code": station_public_code}
        ).fetchall()
        columns = self.get_column_names()
        connections = [self.dict_factory(row, columns) for row in rows]
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
        rows = self.execute(
            """
            SELECT *
            FROM transfer 
            WHERE transfer_station_code = (
                SELECT transfer_station_code 
                FROM transfer 
                WHERE station_public_code = :station_public_code
            )
            AND line_id <> :line_id
            """, 
            {"station_public_code": station_public_code, "line_id": line_id}
        ).fetchall()
        columns = self.get_column_names()
        transfer_info = [self.dict_factory(row, columns) for row in rows]
        return transfer_info
    
    def get_timetable(self, station_public_code: str) -> list[dict]:
        """Query timetable information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: timetable information
        """
        
        rows = self.execute(
            """
            SELECT * 
            FROM final_timetable 
            WHERE station_public_code = :station_public_code
            """, 
            {"station_public_code": station_public_code}
        ).fetchall()
        columns = self.get_column_names()
        timetable_info = [self.dict_factory(row, columns) for row in rows]
        return timetable_info
    
if __name__ == "__main__":
    timetable_db_manager = TimetableDBManager()
    import time
    start = time.time()
    station_public_code = "123" # 회기역
    day_code = 8
    print(
        [
            row[0] 
            for row in timetable_db_manager.execute(
                "SELECT DISTINCT realtime_train_id FROM final_timetable WHERE station_public_code = :station_public_code AND day_code = :day_code", 
                {"station_public_code":station_public_code, "day_code": day_code}
            ).fetchall()
        ],
        f"\n{time.time() - start:.05f}s...."
    )