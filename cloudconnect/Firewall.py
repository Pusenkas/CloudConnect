from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network
from .Component import Component


@dataclass
class Firewall:
    name: str
    rules: dict[(IPv4Network, IPv4Network, int), bool] = field(default_factory= lambda: {})

    def add_rule(self, src_ip: IPv4Network, dst_ip: IPv4Network, dst_port: int, accept: bool):
        self.rules[(src_ip, dst_ip, dst_port)] = accept
        
    def get_rule(self, src_ip: IPv4Address, dst_ip: IPv4Address, dst_port: int) -> bool:
        for (rule_src_ip, rule_dst_ip, rule_dst_port), accept in self.rules.items():
            if (dst_port == rule_dst_port and src_ip in rule_src_ip and dst_ip in rule_dst_ip):
                return accept
        return True
        
