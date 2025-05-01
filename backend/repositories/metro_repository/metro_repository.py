from abc import ABC, abstractmethod

class MetroRepository(ABC):
    
    @abstractmethod
    def create_engine(self, db_url: str):
        pass
    
    @abstractmethod
    def dispose(self):
        pass
    
    @abstractmethod
    def find_stations_searchbar(self) -> list[dict]:
        """Get all searchbar station

        Returns:
            list[dict]: station searchbar information
        """
        pass
    
    @abstractmethod
    def find_total_station_info(self, station_public_code: str) -> dict:
        '''
            Return station information
                1. station_name
                2. line_info
                    1. line_id
                    2. line_name
                    3. line_color
                3. transfer_lines
                4. adjacent_stations
        '''
        pass
    

    @abstractmethod
    def find_line(self, line_id: int) -> dict:
        """Query line information

        Args:
            line_id (int): an unique line id

        Returns:
            dict: line information
        """
        pass
    
    @abstractmethod
    def find_station(self, station_public_code: str) -> dict:
        """Query station information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            dict: station information
        """
        pass
    
    @abstractmethod
    def find_adjacent_stations(self, station_public_code: str) -> list[dict]:
        """Query connections information

        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: adjacent station information
        """
        pass
    
    def find_transfer_lines(self, line_id: int, station_public_code: str) -> list[dict]:
        """ Query transfer lines.
            Information about same stations of other lines.
            
        Args:
            station_public_code (str): an unique station public code

        Returns:
            list[dict]: adjacent station information
            adjacent_station = {
                
            }
        """
        
    
    

