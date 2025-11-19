from __future__ import annotations

from .base import NetworkDeviceDriver, register_driver

import re
from typing import Generator, Iterable, Dict, Tuple
from ipaddress import ip_network, ip_address

@register_driver("mellanox")
class MellanoxDriver(NetworkDeviceDriver):
    @property
    def comment_symbol(self) -> str:
        return "#"
    
    def show_vlans(self) -> str:
        return "show vlan"
    
    def show_routes(self) -> str:
        return "show ip route static"
    
    def process_vlans(self, output: Iterable[str]) -> Dict[int, str]:
        vlans = {}
        
        for line in output:
            
            if line == "":
                continue
            
            if not line[0].isdigit():
                continue
            
            vlan_id = int(line[0:9].strip())
            vlan_name = line[10:36].strip()
            if vlan_id == 1:
                continue
            vlans[vlan_id] = vlan_name

        return vlans

    def process_routes(self, output: Iterable[str]) -> Iterable[Tuple[ip_network, ip_address]]:
        for line in output:

            if not re.match(r'^\s{2}(default|\d+\.\d+\.\d+\.\d+|[0-9a-f]{4}:)', line):
                continue

            parts = re.split(r'\s+', line.strip())
            
            if parts[0] == "default":
                continue
            
            destination_net = parts[0]
            destination_mask = parts[1]
            gateway = parts[2]
            
            destination = ip_network(f"{destination_net}/{destination_mask}")
            gateway = ip_address(gateway)
            yield (destination, gateway)

    def _create_vlan(self, vlan_id: int, name: str) -> Generator[str, None, None]:
        yield "configure terminal"
        yield f"vlan {vlan_id}"
        if name:
            yield f"name {name}"
        yield "exit"
        yield "exit"

    def _delete_vlan(self, vlan_id: int) -> Generator[str, None, None]:
        yield "configure terminal"
        yield f"no vlan {vlan_id}"
        yield "exit"

    def _rename_vlan(self, vlan_id: int, name: str) -> Generator[str, None, None]:
        yield "configure terminal"
        yield f"vlan {vlan_id}"
        yield f"name {name}"
        yield "exit"
        yield "exit"

    def _create_route(self, destination: ip_network, gateway: ip_address) -> Generator[str, None, None]:
        yield "configure terminal"
        yield f"ip route {str(destination)} {str(gateway)}"
        yield "exit"

    def _delete_route(self, destination: ip_network, gateway: ip_address) -> Generator[str, None, None]:
        yield "configure terminal"
        yield f"no ip route {str(destination)} {str(gateway)}"
        yield "exit"

    def _save(self) -> Generator[str, None, None]:
        yield "write memory"
