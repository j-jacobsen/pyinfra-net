from __future__ import annotations

from .base import NetworkDeviceDriver, register_driver
from typing import Generator, Iterable, Dict, Tuple
from ipaddress import ip_network, ip_address


@register_driver("netgear_prosafe")
class NetgearProsafeDriver(NetworkDeviceDriver):
    @property
    def comment_symbol(self) -> str:
        return "!"
    
    @property
    def expect_string(self) -> str:
        return r"\(.*\)\s*(\((Vlan|Config)\))?#"
    
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
            
            parts = line.split()
            vlan_id = int(parts[0])
            vlan_name = parts[1]

            if vlan_name == "VLAN"+str(vlan_id):
                vlan_name = ""
            
            if vlan_id == 1:
                continue
            
            vlans[vlan_id] = vlan_name

        return vlans
    
    def process_routes(self, output: Iterable[str]) -> Iterable[Tuple[ip_network, ip_address]]:
        for line in output:

            if line == "":
                continue
            
            if not line[0] == "S":
                continue
            
            parts = line.split()
            
            if parts[1] == "0.0.0.0/0":
                continue
            
            destination = ip_network(parts[1])
            gateway = ip_address(parts[4].replace(",", ""))
            yield (destination, gateway)

    def _create_vlan(self, vlan_id: int, name: str) -> Generator[str, None, None]:
        yield "vlan database"
        yield f"vlan {vlan_id}"
        if name:
            yield f"vlan name {vlan_id} {name}"
        yield "exit"

    def _delete_vlan(self, vlan_id: int) -> Generator[str, None, None]:
        yield "vlan database"
        yield f"no vlan {vlan_id}"
        yield "exit"

    def _rename_vlan(self, vlan_id: int, name: str) -> Generator[str, None, None]:
        yield "vlan database"
        yield f"vlan name {vlan_id} {name}"
        yield "exit"

    def _create_route(self, destination: ip_network, gateway: ip_address) -> Generator[str, None, None]:
        yield "configure"
        yield f"ip route {str(destination.network_address)} {str(destination.netmask)} {str(gateway)}"
        yield "exit"

    def _delete_route(self, destination: ip_network, gateway: ip_address) -> Generator[str, None, None]:
        yield "configure"
        yield f"no ip route {str(destination.network_address)} {str(destination.netmask)} {str(gateway)}"
        yield "exit"

    def _save(self) -> Generator[str, None, None]:
        yield "write memory confirm"