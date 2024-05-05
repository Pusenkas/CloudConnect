from dataclasses import dataclass, field
from copy import deepcopy
from ipaddress import IPv4Address
import networkx as nx
from .NAT import NAT
from .Component import Component
from .Firewall import Firewall


@dataclass
class ConnectionData:
    src_ip: IPv4Address
    dst_ip: IPv4Address
    src_port: int
    dst_port: int

    def __iter__(self):
        yield from (self.src_ip, self.dst_ip, self.src_port, self.dst_port)


@dataclass
class Orchestrator:
    pool: nx.Graph
    tags = ("__SRC__IP__", "__DST__IP__", "__SRC__PORT__", "__DST__PORT__")

    def get_data(self, name: str, request_from_comp) -> dict | None:
        '''Gets data for establishing connection with component using specified name'''
        comp = self.pool.nodes[name]["value"]
        connection_data = ConnectionData(src_ip=request_from_comp.ip, dst_ip=comp.ip,
                                         src_port=request_from_comp.port, dst_port=comp.port)
        path = next(nx.shortest_simple_paths(self.pool, name, request_from_comp.name))

        for i, node_name in enumerate(path[1:-1], start=1):
            match self.pool.nodes[node_name]["value"]:
                case NAT() as x:
                    if self.pool[path[i]][path[i + 1]]["value"] == x.name: # transform src
                        pass
                    if self.pool[path[i - 1]][path[i]]["value"] == x.name: # transform dst
                        connection_data.dst_port = x.find_rule(connection_data.dst_ip, connection_data.dst_port)
                        connection_data.dst_ip = x.ip
                case Firewall() as x:
                    if self.pool[path[i]][path[i + 1]]["value"] == x.name: # transform src
                        pass
                    if self.pool[path[i - 1]][path[i]]["value"] == x.name: # transform dst
                        accept = x.get_rule(connection_data.src_ip, connection_data.dst_ip, connection_data.dst_port)
                        if not accept:
                            raise ConnectionError("Firewall error")
                case Component() as x:
                    pass
                case _:
                    pass
        data = deepcopy(comp.connect_data)
        for value, tag in zip(connection_data, self.tags):
            Orchestrator._prepare_data(data, tag, value)
        return data

    def _prepare_data(data, lookup_key, value):
        '''Orchestrates data'''
        if isinstance(data, dict):
            for k, v in data.items():
                if v == lookup_key:
                    data[k] = value
                else:
                    Orchestrator._prepare_data(v, lookup_key, value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if item == lookup_key:
                    data[i] = value
                else:
                    Orchestrator._prepare_data(item, lookup_key, value)
