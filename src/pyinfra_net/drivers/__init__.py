from __future__ import annotations

from typing import Optional

from .base import NetworkDeviceDriver, register_driver, get_driver_class

from . import netgear_prosafe
from . import mellanox

def get_driver(name: str, debug: Optional[bool] = False) -> NetworkDeviceDriver:
    try:
        driver = get_driver_class(name)
        instance = driver()
        instance.debug = debug
        return instance
    except KeyError:
        raise NotImplementedError(f"Unsupported device type: {name}")

__all__ = [ 
    "NetworkDeviceDriver",
    "register_driver",
    "get_driver",
    "get_driver_class",
]