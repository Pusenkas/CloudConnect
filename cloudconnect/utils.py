import random
from ipaddress import ip_address


def random_ip() -> ip_address:
    '''Generate random ip'''
    return ip_address(random.randint(1, 0xffffffff))


def random_port() -> int:
    '''Generate random port in range (1, 65536)'''
    return random.randint(1, 0xffff)
