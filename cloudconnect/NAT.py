from dataclasses import dataclass, field
from ipaddress import ip_address, IPv4Address, IPv4Network
from .Component import Component


@dataclass
class NAT:
    name: str
    ip: IPv4Address
    network: IPv4Network
    rules: dict[int, (ip_address, int)] = field(default_factory=lambda: {})
    _available_ips: set[ip_address] = field(init=False, repr=False)
    _available_ports: set[int] = field(init=False, repr=False)

    def __post_init__(self):
        self._available_ips = set(self.network.hosts())
        self._available_ports = {i for i in range(1024, 65536)}

    def add_rule(self, local_ip: IPv4Address, port: int):
        '''Adds nat rule'''
        if local_ip not in self._available_ips:
            raise ConnectionError("Wrong ip_address")
        self._available_ips.remove(local_ip)
        nat_port = self._available_ports.pop()
        self.rules[nat_port] = (local_ip, port)
        
    def add_rule_manual(self, local_ip: IPv4Address, port: int, nat_port: int):
        '''Adds nat rule with specified nat_port'''
        if local_ip not in self._available_ips:
            raise ConnectionError("Wrong ip address for NAT")
        self._available_ips.remove(local_ip)
        if nat_port not in self._available_ports:
            raise ConnectionError("Wrong port for NAT")
        self._available_ports.remove(nat_port)
        self.rules[nat_port] = (local_ip, port)
        
    def find_rule(self, ip: IPv4Address, port: int) -> int:
        '''Returns port according to appropriate rule'''
        for nat_port, (local_ip, local_port) in self.rules.items():
            if local_ip == ip and local_port == port:
                return nat_port
