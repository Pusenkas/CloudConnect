from dataclasses import dataclass, field
from ipaddress import ip_address, IPv4Address, IPv4Network
from .Orchestrator import Orchestrator
from .Component import Component


@dataclass(init=False)
class NAT:
    name: str
    ip: IPv4Address
    network: IPv4Network
    rules: dict[int, (ip_address, int)]
    _under: list[Component]
    _available_ips: set[ip_address] = field(repr=False)
    _available_ports: set[int] = field(repr=False)

    def __init__(self, name, ip, network):
        self.name = name
        self.ip = ip
        self.network = network
        self._under = []
        self.rules = {}
        self._available_ips = set(network.hosts())
        self._available_ports = {i for i in range(1024, 65536)}

    def add_under_nat(self, name: str, port: int, local_ip: IPv4Address = None, data: dict = {}, type: str = "app"):
        '''Add component under NAT'''
        if local_ip and local_ip in self._available_ips:
            self._available_ips.remove(local_ip)
        else:
            local_ip = self._available_ips.pop()
        nat_port = self._available_ports.pop()
        self.rules[nat_port] = (local_ip, port)
        self._under.append(Component(name, type, None, local_ip, port, data))

    def register(self, orchestrator: Orchestrator):
        '''Register NAT in Orchestrator'''
        orchestrator.nats.append(self)
