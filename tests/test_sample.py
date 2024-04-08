import sys
sys.path.append(".")

from cloudconnect.utils import random_ip, random_port
from cloudconnect.NAT import NAT
from cloudconnect.Component import Component
from cloudconnect.Orchestrator import Orchestrator
from ipaddress import ip_address, ip_network
import networkx as nx


class TestClass:
    def test_no_network_functions(self):
        app1 = Component("app 1", "app", None, ip1 := random_ip(), port1 := random_port(), connect_data={
            'ip_to': "__DST__IP__", "ip_from": "__SRC__IP__", "port_to": "__DST__PORT__", 'port_from': "__SRC__PORT__"})
        app2 = Component("app 2", "app", None, ip2 := random_ip(), port2 := random_port(), connect_data={
            'ip_to': "__DST__IP__", "ip_from": "__SRC__IP__", "port_to": "__DST__PORT__", 'port_from': "__SRC__PORT__"})

        g = nx.Graph()
        g.add_nodes_from([(app.name, {"value": app}) for i, app in enumerate((app1, app2))])
        g.add_edges_from(
            [("app 1", "app 2", {"value": 0})])

        orchestrator = Orchestrator(g)
        res = app1.get_data(orchestrator, "app 2")

        assert res, {'ip_to': ip2, "ip_from": ip1, "port_to": ip2, 'port_from': ip1}

    def test_nat(self):
        app1 = Component("app 1", "app", None, ip := random_ip(), port := random_port(), connect_data=None)
        app2 = Component("router", "app", None, ip := random_ip(), port := random_port(), connect_data=None)
        app3 = Component("app 3", "app", None, ip := ip_address("10.0.10.1"), port := 80, connect_data={
            "port": "__DST__PORT__", "ssh": "ssh_key", "ip": "__DST__IP__"})
        nat = NAT("nat1", ip := random_ip(), ip_network("10.0.10.0/24"))
        nat.add_rule(ip_address("10.0.10.1"), 80)

        g = nx.Graph()
        g.add_nodes_from([(app.name, {"value": app}) for i, app in enumerate((app1, app2, nat, app3))])
        g.add_edges_from(
            [("app 1", "router", {"value": 0}),   # ▁▁▁▁         ______        ___        _____
             ("router", "nat1", {"value": 0}),    # |app 1| ---- |router| ---- |nat| ---- |app 3|
             ("nat1", "app 3", {"value": 1})])    # ▔▔▔        ▔▔▔▔       ▔▔       ▔▔▔
        orchestrator = Orchestrator(g)
        res = orchestrator.get_data("app 3", app1)

        assert res, {"port": 1024, "ssh": "ssh_key", "ip": ip}
