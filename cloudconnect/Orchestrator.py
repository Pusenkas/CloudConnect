from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class Orchestrator:
    pool: list = field(default_factory=lambda: [])
    nats: list = field(default_factory=lambda: [])
    dns: list = field(default_factory=lambda: [])
    firewals: list = field(default_factory=lambda: [])
    vpns: list = field(default_factory=lambda: [])

    def get_data(self, name: str, request_from_comp = None) -> dict | None:
        '''Get data for establishing connection with component with specified name'''
        
        for comp in self.pool:
            if comp.name == name:
                if comp.url == None:
                    return comp.connect_data
                for dns in self.dns:
                    for name, addr in dns.rules.items():
                        if name == comp.url:
                            data = deepcopy(comp.connect_data)
                            Orchestrator._parse_data(data, "__URL__", comp.url, addr)
                            return data
                return comp.connect_data
        for nat in self.nats:
            for comp_under_nat in nat._under:
                if comp_under_nat.name == name:
                    for port, (ip, port_under) in nat.rules.items():
                        if ip == comp_under_nat.ip and port_under == comp_under_nat.port:
                            data = deepcopy(comp_under_nat.connect_data)
                            # print("BEFORE", data)
                            Orchestrator._parse_data(
                                data, "__IP_ADDRESS__", comp_under_nat.ip, nat.ip)
                            Orchestrator._parse_data(
                                data, "__PORT__", comp_under_nat.port, port)
                            # print("AFTER", data)
                            return data
        for firewall in self.firewals:
            for comp in firewall._under:
                if comp.name == name:
                    for (src_ip, dst_ip, dst_port), accept in firewall.rules.items():
                        if (comp.port == dst_port and request_from_comp.ip in src_ip.hosts() and comp.ip in dst_ip):
                            data = deepcopy(comp.connect_data)
                            Orchestrator._parse_data(data, "__FIREWALL__", "True", str(accept))
                            return data
                    data = deepcopy(comp.connect_data)
                    Orchestrator._parse_data(data, "__FIREWALL__", "True", "True")
                    return data
        for vpn in self.vpns:
            for comp, key in vpn._under:
                if comp.name == name:
                    data = deepcopy(comp.connect_data)
                    Orchestrator._parse_data(data, "__VPN__", None, key)
                    return data
                        
        return None

    def _parse_data(data, lookup_key, check, value):
        '''Modify connection data to be sufficient'''
        
        if isinstance(data, dict):
            for k, v in data.items():
                if v == {lookup_key: check}:
                    data[k] = value
                else:
                    Orchestrator._parse_data(v, lookup_key, check, value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if item == {lookup_key: check}:
                    data[i] = value
                else:
                    Orchestrator._parse_data(item, lookup_key, check, value)
