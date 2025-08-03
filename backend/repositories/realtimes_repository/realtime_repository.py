from abc import ABC, abstractmethod

class RealtimeRepository(ABC):
    
    @abstractmethod
    def create_engine(self, db_url):
        pass
    
    @abstractmethod
    def dispose(self):
        pass
    
    @abstractmethod
    def upsert_realtimes(self, data: list[dict]):
        """ Insert data to realtime data
        """
        pass
    
    @abstractmethod
    def remove_realtimes(self, op_date: str):
        """ Remove all data from realtime data
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