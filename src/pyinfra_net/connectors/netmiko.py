from netmiko import ConnectHandler
from pyinfra.connectors.base import BaseConnector
from pyinfra.connectors.util import CommandOutput, OutputLine
from pyinfra_net.drivers import get_driver
import click

class NetmikoConnector(BaseConnector):
    handles_execution = True

    @staticmethod
    def make_names_data(hostname):
        yield "@netmiko/{}".format(hostname), {}, []

    def connect(self):
        kwargs = {
            'device_type': self.host.data.get('device_type'),
            'host': self.host.data.get('netmiko_hostname') or self.host.name,
            'username': self.host.data.get('username') or 'admin',
            'password': self.host.data.get('password') or None,
            'port': self.host.data.get('port') or 22,
            'secret': self.host.data.get('enable_password') or None,
            'verbose': False,
        }

        self.connection = ConnectHandler(**kwargs)

    def disconnect(self):
        pass

    def run_shell_command(self, command, print_output=False, print_input=False, **arguments):
        command_str = str(command)
        lines = [ line for line in command_str.splitlines() if line.strip() ]

        if print_input:
            for line in lines:
                click.echo("{0}>>> {1}".format(self.host.print_prefix, line), err=True)

        expect_string = get_driver(self.host.data.get('device_type')).expect_string

        if len(lines) > 1:
            output = self.connection.send_config_set(lines, expect_string=expect_string)
        else:
            output = self.connection.send_command(command_str, expect_string=expect_string)
        
        if print_output and output:
            click.echo("{0}{1}".format(self.host.print_prefix, output), err=True)

        return True, CommandOutput([OutputLine("stdout", line) for line in output.splitlines()])
    
    def put_file(self, filename_or_io, remote_filename, remote_temp_filename, print_output=False, print_input=False, **arguments):
        return False
    
    def get_file(self, filename_or_io, remote_filename, remote_temp_filename, print_output=False, print_input=False, **arguments):
        return False
    
    def check_can_rsync(self):
        raise NotImplementedError("Netmiko connector does not support rsync")