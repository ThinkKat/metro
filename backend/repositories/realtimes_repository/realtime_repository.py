from abc import ABC, abstractmethod

class RealtimeRepository(ABC):
    
    @abstractmethod
    def connect(self, db_url):
        pass
    
    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod
    def insert_realtimes(self, data: list[dict]):
        """ Insert data to realtime data
        """
        pass
    
    @abstractmethod
    def find_realtimes(self, op_date: str)  -> list[dict]:
        """ Find all data of a specified date

        Args:
            op_date (str): _description_

        Returns:
            list[dict]: _description_
        """
        pass