from pyinfra.api import operation
from pyinfra import host
from pyinfra_net.facts import switch
from pyinfra_net.drivers import get_driver

from typing import Optional, Generator, Dict, List, Tuple
from ipaddress import ip_network, ip_address


def _sanitize_vlan_name(name: str) -> str:
    return name[0:32]


@operation()
def vlan(vlan_id: int, name: Optional[str] = "", present: Optional[bool] = True, debug: Optional[bool] = False) -> Generator[str, None, None]: 
    existing_vlans = host.get_fact(switch.Vlans)
    name = _sanitize_vlan_name(name)
    
    drv = get_driver(host.data.get("device_type"), debug)

    if present and vlan_id not in existing_vlans:
        yield from drv.create_vlan(vlan_id, name)
        yield from drv.save()
        return
    elif present and vlan_id in existing_vlans and name != existing_vlans[vlan_id]:
        yield from drv.change_vlan_name(vlan_id, name)
        yield from drv.save()
        return
    elif not present and vlan_id in existing_vlans:
        yield from drv.delete_vlan(vlan_id)
        yield from drv.save()
        return


@operation()
def vlans(vlans: Dict[int, str], debug: Optional[bool] = False):
    vlans = { int(vlan_id): _sanitize_vlan_name(name) for vlan_id, name in vlans.items() }
    existing_vlans = host.get_fact(switch.Vlans)
    
    drv = get_driver(host.data.get("device_type"), debug)

    to_delete = [vlan_id for vlan_id in existing_vlans if vlan_id not in vlans]
    to_create = {vlan_id: vlans[vlan_id] for vlan_id in vlans if vlan_id not in existing_vlans}
    to_rename = {vlan_id: vlans[vlan_id] for vlan_id in vlans if vlan_id in existing_vlans and vlans[vlan_id] != existing_vlans[vlan_id]}

    for vlan_id in to_delete:
        yield from drv.delete_vlan(vlan_id)

    for vlan_id, name in to_create.items():
        yield from drv.create_vlan(vlan_id, name)

    for vlan_id, name in to_rename.items():
        yield from drv.rename_vlan(vlan_id, name)

    if to_delete or to_create or to_rename:
        yield from drv.save()


@operation()
def route(destination: str, gateway: str, present: Optional[bool] = True, debug: Optional[bool] = False):
    existing_routes = host.get_fact(switch.Routes)
    destination = ip_network(destination)
    gateway = ip_address(gateway)
    route = (destination, gateway)

    drv = get_driver(host.data.get("device_type"), debug)

    if present and route not in existing_routes:
        yield from drv.create_route(destination, gateway)
        yield from drv.save()
        return
    elif not present and route in existing_routes:
        yield from drv.delete_route(destination, gateway)
        yield from drv.save()
        return


@operation()
def routes(routes: List[Tuple[str, str]], debug: Optional[bool] = False):
    existing_routes = host.get_fact(switch.Routes)
    desired_routes = [ (ip_network(destination), ip_address(gateway)) for destination, gateway in routes ]

    drv = get_driver(host.data.get("device_type"), debug)

    to_delete = [ route for route in existing_routes if route not in desired_routes ]
    to_create = [ route for route in desired_routes if route not in existing_routes ]

    for destination, gateway in to_delete:
        yield from drv.delete_route(destination, gateway)

    for destination, gateway in to_create:
        yield from drv.create_route(destination, gateway)

    if to_delete or to_create:
        yield from drv.save()