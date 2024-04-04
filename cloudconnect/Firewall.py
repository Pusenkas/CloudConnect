from dataclasses import dataclass
from ipaddress import IPv4Address, IPv4Network
from .Orchestrator import Orchestrator
from .Component import Component


@dataclass
class Firewall:
    name: str
    rules: dict[(IPv4Network, IPv4Network, int), bool]
    _under: list[Component]

    def add_under_firewall(self, name: str, port: int, local_ip: IPv4Address, data: dict = {}, type: str = "app"):
        '''Add component under Firewall'''
        self._under.append(Component(name, type, None, local_ip, port, data))

    def add_rule(self, src_ip: IPv4Network, dst_ip: IPv4Network, dst_port: int, accept: bool):
        self.rules[(src_ip, dst_ip, dst_port)] = accept

    def register(self, orchestrator: Orchestrator):
        '''Register Firewall in Orchestrator'''
        orchestrator.firewals.append(self)
