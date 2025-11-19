from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generator, Iterable, Type, Dict, Optional, Tuple
from ipaddress import ip_network, ip_address


class NetworkDeviceDriver(ABC):
    debug: bool = False

    @abstractmethod
    def show_vlans(self) -> str:
        pass

    @abstractmethod
    def show_routes(self) -> str:
        pass

    @abstractmethod
    def process_vlans(self, output: Iterable[str]) -> Dict[int, str]:
        pass

    @abstractmethod
    def process_routes(self, output: Iterable[str]) -> Iterable[Tuple[ip_network, ip_address]]:
        pass

    def expect_string(self) -> Optional[str]:
        return None

    def create_vlan(self, vlan_id: int, name: str) -> Generator[str, None, None]:
        if vlan_id == 1:
            return
        if self.debug:
            yield from self.comment(self._create_vlan(vlan_id, name))
        else:
            yield from self._create_vlan(vlan_id, name)

    def delete_vlan(self, vlan_id: int) -> Generator[str, None, None]:
        if vlan_id == 1:
            return
        if self.debug:
            yield from self.comment(self._delete_vlan(vlan_id))
        else:
            yield from self._delete_vlan(vlan_id)

    def rename_vlan(self, vlan_id: int, name: str) -> Generator[str, None, None]:
        if vlan_id == 1:
            return
        if self.debug:
            yield from self.comment(self._change_vlan_name(vlan_id, name))
        else:
            yield from self._change_vlan_name(vlan_id, name)

    def create_route(self, destination: ip_network, gateway: ip_address) -> Generator[str, None, None]:
        if self.debug:
            yield from self.comment(self._create_route(destination, gateway))
        else:
            yield from self._create_route(destination, gateway)

    def delete_route(self, destination: ip_network, gateway: ip_address) -> Generator[str, None, None]:
        if self.debug:
            yield from self.comment(self._delete_route(destination, gateway))
        else:
            yield from self._delete_route(destination, gateway)

    def save(self) -> Generator[str, None, None]:
        if self.debug:
            yield from self.comment(self._save())
        else:
            yield from self._save()

    def comment(self, commands: Iterable[str]) -> Generator[str, None, None]:
        for command in commands:
            yield f"{self.comment_symbol} {command}"

    @property
    @abstractmethod
    def comment_symbol(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _create_vlan(self, vlan_id: int, name: str) -> Generator[str, None, None]:
        pass

    @abstractmethod
    def _delete_vlan(self, vlan_id: int) -> Generator[str, None, None]:
        pass

    @abstractmethod
    def _rename_vlan(self, vlan_id: int, name: str) -> Generator[str, None, None]:
        pass

    @abstractmethod
    def _create_route(self, destination: ip_network, gateway: ip_address) -> Generator[str, None, None]:
        pass

    @abstractmethod
    def _delete_route(self, destination: ip_network, gateway: ip_address) -> Generator[str, None, None]:
        pass

    @abstractmethod
    def _save(self) -> Generator[str, None, None]:
        pass


_DRIVER_REGISTRY: Dict[str, Type[NetworkDeviceDriver]] = {}


def register_driver(name: str):
    def decorator(cls: Type[NetworkDeviceDriver]) -> Type[NetworkDeviceDriver]:
        _DRIVER_REGISTRY[name] = cls
        return cls
    
    return decorator


def get_driver_class(name: str) -> Type[NetworkDeviceDriver]:
    try:
        return _DRIVER_REGISTRY[name]
    except KeyError:
        raise NotImplementedError(f"Unsupported device type: {name}")