from abc import ABC, abstractmethod

class TimetableRepository(ABC):
    
    @abstractmethod
    def create_engine(self, db_url):
        pass
    
    @abstractmethod
    def dispose(self):
        pass
    
    @abstractmethod
    def find_timetable_for_calculation_delay(self, op_date: str, day_code: int) -> list[dict]:
        """Query timetable information for calculation delay.
        This method is used to find timetable information for calculation delay.
        It will return all timetable information that is valid for the given operation date.
        The timetable information is used to calculate the delay of the train.
        
        Args:
            op_date (str): operation date

        Returns:
            list[dict]: timetable information
        """
        pass
    
    @abstractmethod
    def find_timetable_by_station_public_code(self, op_date: str, station_public_code: str) -> list[dict]:
        """Query timetable information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: timetable information
        """
        pass
    
    