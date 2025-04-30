from abc import ABC, abstractmethod

class TimetableRepository(ABC):
    
    @abstractmethod
    def connect(self, db_url):
        pass
    
    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod
    def find_timetable(self, op_date: str, station_public_code: str) -> list[dict]:
        """Query timetable information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: timetable information
        """
        pass