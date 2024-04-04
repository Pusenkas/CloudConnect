from dataclasses import dataclass
from ipaddress import IPv4Address
from .Orchestrator import Orchestrator


@dataclass(frozen=True)
class Component:
    name: str
    type: str
    url: str
    ip: IPv4Address
    port: int
    connect_data: dict

    def register(self, orchestrator: Orchestrator):
        '''Register Component in Orchestrator'''
        orchestrator.pool.append(self)

    def get_data(self, orchestrator: Orchestrator, name: str) -> dict | None:
        '''This method is not used right now'''
        # for comp in orchestrator.pool:
        #   if comp.ip == ip_other:
        #        return True
        # return False
        return orchestrator.get_data(name, self)
    
