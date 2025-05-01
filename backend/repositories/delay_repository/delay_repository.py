from abc import ABC, abstractmethod

class DelayRepository(ABC):
    
    @abstractmethod
    def create_engine(self, db_url):
        pass
    
    @abstractmethod
    def dispose(self):
        pass
    
    @abstractmethod
    def insert_delay(self, data: list[dict]):
        """ Insert delay data
        """
        pass