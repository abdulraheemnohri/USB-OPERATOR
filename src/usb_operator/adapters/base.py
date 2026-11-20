from abc import ABC,abstractmethod
from ..models import Device
class DeviceAdapter(ABC):
    transport:str
    @abstractmethod
    async def discover(self)->list[Device]: raise NotImplementedError
    async def execute(self,device:Device,action:str,parameters:dict)->dict: raise NotImplementedError(f"{self.transport} adapter does not implement control.")
