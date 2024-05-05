from ipaddress import ip_address, ip_network

from cloudconnect.Orchestrator import Orchestrator
from cloudconnect.Component import Component
from cloudconnect.Firewall import Firewall
from cloudconnect.NAT import NAT
from cloudconnect.VPN import VPN
from cloudconnect.DNS import DNS
from cloudconnect.utils import random_ip, random_port

import networkx as nx
import matplotlib.pyplot as plt
from pprint import pprint


def test_dns():  # todo
    orchestrator = Orchestrator()
    app1 = Component("application 1", "app", None, ip := random_ip(), port := random_port(), connect_data={
                     'ip': ip, 'port': port})
    app2 = Component("application 2", "app", None, ip := random_ip(), port := random_port(), connect_data={
                     'ip': ip, 'port': port})
    app3 = Component("application 3", "app", "my.host", ip := random_ip(), port := random_port(), connect_data={
                     'my_url_address': {"__URL__": "my.host"}, 'port': port})
    app1.register(orchestrator)
    app2.register(orchestrator)
    app3.register(orchestrator)

    dns = DNS("dns1", {"my.host": "your.host.com",
                       "google.com": ip_address("74.125.131.139")})
    dns.register(orchestrator)
    res = orchestrator.get_data("application 3")

    print("DNS TEST")
    print(f"Data before orchestration: {app3.connect_data}\nData after orchestration:  {res}\n")


def test_vpn():  # todo
    orchestrator = Orchestrator()
    app1 = Component("application 1", "app", None, ip := ip_address("192.12.13.24"), port :=
                     random_port(), connect_data={'ip': ip_address("192.12.13.24"), 'port': port})
    app2 = Component("application 2", "app", None, ip := random_ip(), port := random_port(), connect_data={
                     'ip': ip, 'port': port})
    app1.register(orchestrator)
    app2.register(orchestrator)

    vpn = VPN("vpn1", ip_network("10.0.10.0/24"), [])
    vpn.add("app3", 80, ip_address("10.0.10.1"), data={"key": {"__VPN__": None}})
    vpn.register(orchestrator)

    res = app1.get_data(orchestrator, "app3")

    print("VPN TEST")
    print(f"Data before orchestration: {vpn._under[0][0].connect_data}\nData after orchestration:  {res}\n")


def main():
    app1 = Component("app 1", "app", None, ip := ip_address("192.12.13.24"), port :=
                     random_port(), connect_data={'ip': ip_address("192.12.13.24"), 'port': port})
    app3 = Component("app 2", "app", None, ip := ip_address("10.0.10.1"), port := 80, connect_data={
                     "port": "__DST__PORT__", "ssh": "ahhahahahahahahahahaah", "ip": "__DST__IP__"})
    nat = NAT("nat", random_ip(), ip_network("10.0.10.0/24"))
    nat.add_rule_manual(ip_address("10.0.10.1"), 80, 1024)
    firewall = Firewall("firewall")
    firewall.add_rule(ip_network("0.0.0.0/0"), ip_network("0.0.0.0/0"), 1024, True)

    g = nx.Graph()
    g.add_nodes_from([(app.name, {"value": app}) for i, app in enumerate((app1, firewall, nat, app3))])
    g.add_edges_from(
        [("app 1", "firewall", {"value": None}),         # ▁▁▁▁        ______          ___        _____
         ("firewall", "nat", {"value": "firewall"}),   # |app 1| ---- |firewall| ---- |nat| ---- |app 3|
         ("nat", "app 2", {"value": "nat"})])           # ▔▔▔       ▔▔▔▔         ▔▔       ▔▔▔
    orchestrator = Orchestrator(g)
    res = app1.get_data(orchestrator, "app 2")
    pprint(res)

    fig = plt.figure()
    edge_color = ['lime' if g[u][v]["value"] else 'cyan' for u, v in g.edges]
    #edge_color = ['b' for u, v in g.edges]
    node_color = ['cyan' if isinstance(node[1]["value"], Component) else 'lime' for node in g.nodes(data=True)]
    nx.draw(g, with_labels=True, edge_color=edge_color, node_color=node_color, ax=fig.add_subplot())
    fig.savefig("graph.png")


if __name__ == "__main__":
    main()
