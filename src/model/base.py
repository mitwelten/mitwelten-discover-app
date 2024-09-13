from abc import ABC, abstractmethod

class BaseDeployment(ABC):
    def __init__(self, id, lat, lon, type):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.type = type


    @abstractmethod
    def to_dict(self):
        pass

