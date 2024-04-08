from dataclasses import dataclass, field
from ipaddress import ip_address, IPv4Address, IPv4Network
from .Component import Component


@dataclass(init=False)
class NAT:
    name: str
    ip: IPv4Address
    network: IPv4Network
    rules: dict[int, (ip_address, int)]
    _available_ips: set[ip_address] = field(repr=False)
    _available_ports: set[int] = field(repr=False)

    def __init__(self, name, ip, network):
        self.name = name
        self.ip = ip
        self.network = network
        self.rules = {}
        self._available_ips = set(network.hosts())
        self._available_ports = {i for i in range(1024, 65536)}

    def add_rule(self, local_ip: IPv4Address, port: int):
        '''Add component under NAT'''
        if local_ip not in self._available_ips:
            raise ConnectionError("Wrong ip_address")
        self._available_ips.remove(local_ip)
        nat_port = self._available_ports.pop()
        self.rules[nat_port] = (local_ip, port)
        
    def find_rule(self, ip: IPv4Address, port: int) -> int:
        for nat_port, (local_ip, local_port) in self.rules.items():
            if local_ip == ip and local_port == port:
                return nat_port

    def register(self, orchestrator):
        '''Register NAT in Orchestrator'''
        orchestrator.nats.append(self)
