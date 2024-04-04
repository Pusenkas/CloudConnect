from ipaddress import ip_address, ip_network

from cloudconnect.Orchestrator import Orchestrator
from cloudconnect.Component import Component
from cloudconnect.Firewall import Firewall
from cloudconnect.NAT import NAT
from cloudconnect.VPN import VPN
from cloudconnect.DNS import DNS
from cloudconnect.utils import random_ip, random_port


def test_no_network_functions():
    orchestrator = Orchestrator()
    app1 = Component("application 1", "app", None, ip := random_ip(), port := random_port(), connect_data={
                     'ip': ip, 'port': port})
    app2 = Component("application 2", "app", None, ip := random_ip(), port := random_port(), connect_data={
                     'ip': ip, 'port': port})
    app1.register(orchestrator)
    app2.register(orchestrator)

    res = app1.get_data(orchestrator, "application 2")

    print("SIMPLE TEST")
    print(f"Data before orchestration: {app2.connect_data}\nData after orchestration:  {res}\n")


def test_nat():
    orchestrator = Orchestrator()
    app1 = Component("application 1", "app", None, ip := random_ip(), port := random_port(), connect_data={
                     'ip': ip, 'port': port})
    app2 = Component("application 2", "app", None, ip := random_ip(), port := random_port(), connect_data={
                     'ip': ip, 'port': port})
    app1.register(orchestrator)
    app2.register(orchestrator)
    nat = NAT("nat1", random_ip(), ip_network("10.0.10.0/24"))
    nat.add_under_nat("app3", 80, local_ip=ip_address("10.0.10.1"), data={"port": {
        "__PORT__": 80}, "ssh": "ahhahahahahahahahahaah", "ip": {"__IP_ADDRESS__": ip_address("10.0.10.1")}})
    nat.register(orchestrator)
    res = orchestrator.get_data("app3")

    print("NAT TEST")
    print(f"Data before orchestration: {nat._under[0].connect_data}\nData after orchestration:  {res}\n")


def test_dns():
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


def test_firewall():
    orchestrator = Orchestrator()
    app1 = Component("application 1", "app", None, ip := ip_address("192.12.13.24"), port :=
                     random_port(), connect_data={'ip': ip_address("192.12.13.24"), 'port': port})
    app2 = Component("application 2", "app", None, ip := random_ip(), port := random_port(), connect_data={
                     'ip': ip, 'port': port})
    app1.register(orchestrator)
    app2.register(orchestrator)

    firewall = Firewall("firewall1", {}, [])
    firewall.add_under_firewall("app3", 80, local_ip=ip_address("192.12.13.42"), data={
        "username": "CoolName123", "firewall": {"__FIREWALL__": "True"}})
    firewall.add_rule(ip_network("192.12.13.24"),
                      ip_network("192.12.13.42"), 80, False)
    firewall.register(orchestrator)
    res = app1.get_data(orchestrator, "app3")

    print("FIREWALL TEST")
    print(f"Data before orchestration: {firewall._under[0].connect_data}\nData after orchestration:  {res}\n")


def test_vpn():
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
    test_no_network_functions()
    test_nat()
    test_dns()
    test_firewall()
    test_vpn()


if __name__ == "__main__":
    main()
