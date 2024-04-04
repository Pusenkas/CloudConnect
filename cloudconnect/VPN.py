import os
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network
from .Orchestrator import Orchestrator
from .Component import Component


@dataclass
class VPN:
    name: str
    network: IPv4Network
    _under: list[(Component, int)]

    def add(self, name: str, port: int, local_ip: IPv4Address, data: dict = {}, type: str = "app"):
        '''Add component under NAT'''
        if local_ip not in self.network.hosts():
            raise ConnectionError("Wrong ip_address")
        self._under.append((Component(name, type, None, local_ip, port, data), os.urandom(16)))

    def register(self, orchestrator: Orchestrator):
        '''Register NAT in Orchestrator'''
        orchestrator.vpns.append(self)
