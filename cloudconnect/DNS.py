from dataclasses import dataclass
from ipaddress import IPv4Address
from .Orchestrator import Orchestrator


@dataclass
class DNS:
    name: str
    rules: dict[str, str | IPv4Address]

    def add_rule(self, resolve_from: str, resolve_to: str | IPv4Address):
        self.rules[resolve_from] = resolve_to

    def register(self, orchestrator: Orchestrator):
        orchestrator.dns.append(self)
