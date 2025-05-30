from abc import ABC, abstractmethod

class DelayRepository(ABC):
    
    @abstractmethod
    def create_engine(self, db_url):
        pass
    
    @abstractmethod
    def dispose(self):
        pass
    
    @abstractmethod
    def insert_delay_all(self, data: list[dict]):
        """ Insert delay data
        """
        pass
    
    @abstractmethod
    def insert_delay_many(self, data: list[dict], data_size: int = 1000):
        """ Insert delay data with data_size
        """
        pass
    
    @abstractmethod
    def find_delay_many_by_op_date(self, op_date: str, size: int = 1000) -> dict:
        """ Select delay data by op date
        """
        pass