from dataclasses import dataclass, field
from copy import deepcopy
import networkx as nx
from .NAT import NAT
from .Component import Component


@dataclass
class Orchestrator:
    pool: nx.Graph
    nats: list = field(default_factory=lambda: [])
    dns: list = field(default_factory=lambda: [])
    firewals: list = field(default_factory=lambda: [])
    vpns: list = field(default_factory=lambda: [])
    tags = ("__SRC_IP__", "__DST__IP__", "__SRC__PORT__", "__DST__PORT__")

    def get_data(self, name: str, request_from_comp) -> dict | None:
        '''Get data for establishing connection with component with specified name'''
        comp = self.pool.nodes[name]["value"]
        data = deepcopy(comp.connect_data)
        path = next(nx.shortest_simple_paths(self.pool, name, request_from_comp.name))

        for key, value in zip(self.tags, (request_from_comp.ip, comp.ip, request_from_comp.port, comp.port)):
            Orchestrator._prepare_data(data, key, value)
        for i, node_name in enumerate(path[1:-1], start=1):
            match self.pool.nodes[node_name]["value"]:
                case NAT() as x:
                    if self.pool[path[i]][path[i + 1]]["value"] == 1:
                        pass
                        #print("transform dest")
                    if self.pool[path[i - 1]][path[i]]["value"] == 1:
                        Orchestrator._parse_data(
                            data, "__DST__IP__", comp.ip, x.ip)
                        Orchestrator._parse_data(
                            data, "__DST__PORT__", comp.port, x.find_rule(comp.ip, comp.port))
                        #print("transform src")
                case Component() as x:
                    pass
                case _:
                    pass
        for tag in self.tags:
            Orchestrator._clear_data(data, tag)
        return data

    def _parse_data(data, lookup_key, check, value):
        '''Modify connection data to be sufficient'''
        if isinstance(data, dict):
            for k, v in data.items():
                if v == {lookup_key: check}:
                    data[k] = {lookup_key: value}
                else:
                    Orchestrator._parse_data(v, lookup_key, check, value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if item == {lookup_key: check}:
                    data[i] = {lookup_key: value}
                else:
                    Orchestrator._parse_data(item, lookup_key, check, value)

    def _clear_data(data, lookup_key):
        '''Remove redundant data in connection data'''
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict) and v.keys() == {lookup_key}:
                    data[k] = v[lookup_key]
                else:
                    Orchestrator._clear_data(v, lookup_key)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(v, dict) and v.keys() == {lookup_key}:
                    data[k] = v[lookup_key]
                else:
                    Orchestrator._clear_data(item, lookup_key)

    def _prepare_data(data, lookup_key, value):
        '''Sets initial values in connection data'''
        if isinstance(data, dict):
            for k, v in data.items():
                if v == lookup_key:
                    data[k] = {lookup_key: value}
                else:
                    Orchestrator._prepare_data(v, lookup_key, value)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if item == lookup_key:
                    data[i] = {lookup_key: value}
                else:
                    Orchestrator._prepare_data(item, lookup_key, value)
