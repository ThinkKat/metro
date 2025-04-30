from abc import ABC, abstractmethod

class DelayRepository(ABC):
    
    @abstractmethod
    def connect(self, db_url):
        pass
    
    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod
    def insert_delay(self, data: list[dict]):
        """ Insert delay data
        """
        pass