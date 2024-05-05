import sys
sys.path.append(".")

from cloudconnect.utils import random_ip, random_port
from cloudconnect.NAT import NAT
from cloudconnect.Firewall import Firewall
from cloudconnect.Component import Component
from cloudconnect.Orchestrator import Orchestrator
from ipaddress import ip_address, ip_network
import networkx as nx
import pytest



class TestClass:
    def test_no_network_functions(self):
        app1 = Component("app 1", "app", None, ip1 := random_ip(), port1 := random_port(), connect_data={
            'ip_to': "__DST__IP__", "ip_from": "__SRC__IP__", "port_to": "__DST__PORT__", 'port_from': "__SRC__PORT__"})
        app2 = Component("app 2", "app", None, ip2 := random_ip(), port2 := random_port(), connect_data={
            'ip_to': "__DST__IP__", "ip_from": "__SRC__IP__", "port_to": "__DST__PORT__", 'port_from': "__SRC__PORT__"})

        g = nx.Graph()
        g.add_nodes_from([(app.name, {"value": app}) for i, app in enumerate((app1, app2))])
        g.add_edges_from(
            [("app 1", "app 2", {"value": None})])

        orchestrator = Orchestrator(g)
        res = app1.get_data(orchestrator, "app 2")
        assert res == {'ip_to': ip2, "ip_from": ip1, "port_to": port2, 'port_from': port1}

    def test_nat(self):
        app1 = Component("app 1", "app", None, ip := random_ip(), port := random_port(), connect_data=None)
        app2 = Component("router", "app", None, ip := random_ip(), port := random_port(), connect_data=None)
        app3 = Component("app 3", "app", None, ip := ip_address("10.0.10.1"), port := 80, connect_data={
            "port": "__DST__PORT__", "ssh": "ssh_key", "ip": "__DST__IP__"})
        nat = NAT("nat1", ip := random_ip(), ip_network("10.0.10.0/24"))
        nat.add_rule_manual(ip_address("10.0.10.1"), 80, 1024)

        g = nx.Graph()
        g.add_nodes_from([(app.name, {"value": app}) for i, app in enumerate((app1, app2, nat, app3))])
        g.add_edges_from(
            [("app 1", "router", {"value": None}),
             ("router", "nat1", {"value": None}),
             ("nat1", "app 3", {"value": "nat1"})]) 
        orchestrator = Orchestrator(g)
        res = app1.get_data(orchestrator, "app 3")
        print(res)
        assert res == {"port": 1024, "ssh": "ssh_key", "ip": ip}

    def test_firewall(self):
        app1 = Component("app 1", "app", None, ip1 := ip_address(
            "10.0.10.1"), port1 := random_port(), connect_data=None)
        app2 = Component("app 2", "app", None, ip2 := ip_address("10.0.10.2"), port2 := 80, connect_data=None)
        firewall = Firewall("firewall")
        firewall.add_rule(ip_network("10.0.10.0/24"), ip_network("10.0.10.0/24"), 80, False)

        g = nx.Graph()
        g.add_nodes_from([(app.name, {"value": app}) for i, app in enumerate((app1, firewall, app2))])
        g.add_edges_from(
            [("app 1", "firewall", {"value": None}),
                ("firewall", "app 2", {"value": "firewall"})])
        orchestrator = Orchestrator(g)
        with pytest.raises(Exception):
            res = app1.get_data(orchestrator, "app 2")

    def test_nat_firewall(self):
        app1 = Component("app 1", "app", None, ip := ip_address("192.12.13.24"), port :=
                         random_port(), connect_data={'ip': ip_address("192.12.13.24"), 'port': port})
        app2 = Component("app 2", "app", None, ip := ip_address("10.0.10.1"), port := 80, connect_data={
            "port": "__DST__PORT__", "ssh": "ssh_key", "ip": "__DST__IP__"})
        nat = NAT("nat1", nat_ip := random_ip(), ip_network("10.0.10.0/24"))
        nat.add_rule_manual(ip_address("10.0.10.1"), 80, 1024)
        firewall = Firewall("firewall1")
        firewall.add_rule(ip_network("0.0.0.0/0"), ip_network("0.0.0.0/0"), 1024, True)

        g = nx.Graph()
        g.add_nodes_from([(app.name, {"value": app}) for i, app in enumerate((app1, firewall, nat, app2))])
        g.add_edges_from(
            [("app 1", "firewall1", {"value": None}),
             ("firewall1", "nat1", {"value": "firewall1"}),
             ("nat1", "app 2", {"value": "nat1"})])
        orchestrator = Orchestrator(g)
        res = app1.get_data(orchestrator, "app 2")
        assert res == {"port": 1024, "ssh": "ssh_key", "ip": nat_ip}
