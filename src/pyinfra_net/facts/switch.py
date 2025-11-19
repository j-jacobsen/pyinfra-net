from pyinfra.api import FactBase
from pyinfra import host
from pyinfra_net.drivers import get_driver

class Vlans(FactBase):
    def command(self):
        return get_driver(host.data.get("device_type")).show_vlans()

    def process(self, output):
        return get_driver(host.data.get("device_type")).process_vlans(output)

class Routes(FactBase):
    def command(self):
        return get_driver(host.data.get("device_type")).show_routes()

    def process(self, output):
        return list(get_driver(host.data.get("device_type")).process_routes(output))
    