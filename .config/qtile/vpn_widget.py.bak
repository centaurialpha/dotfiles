import subprocess
from libqtile.command.base import expose_command

from libqtile.widget import base


class VPN(base._TextBox):
    defaults = [
        ("iface", None, "Interface"),
    ]

    def __init__(self, **config):
        super().__init__("•", **config)
        self.iface = config.get("iface", "")
        self.add_callbacks({"Button1": self.trigger})
        self._init()

    def _toggle(self):
        if self.state == "on":
            self.state = "off"
            self.foreground = "#ff0000"
        else:
            self.state = "on"
            self.foreground = "#00ff00"

    def _init(self):
        output = subprocess.check_output(["ip", "link"])
        if self.iface in output.decode():
            self.state = "on"
            self.foreground = "#00ff00"
        else:
            self.state = "off"
            self.foreground = "#ff0000"

    @expose_command
    def trigger(self):
        if self.state == "on":
            subprocess.run(["vpn", self.iface, "off"])
        else:
            subprocess.run(["vpn", self.iface, "on"])
        self._toggle()
        self.draw()
