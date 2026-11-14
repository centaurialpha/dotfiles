"""
Widgets that redraw with D-Bus PropertiesChanged signals, without polling
"""

from collections.abc import Callable
from typing import Any

from dbus_fast import (
    BusType,
    Message,
)
from dbus_fast.aio import MessageBus
from libqtile.utils import add_signal_receiver
from qtile_extras import widget

PROPERTIES_INTERFACE = "org.freedesktop.DBus.Properties"


async def watch_properties(
    callback: Callable[[Message], None],
    *,
    path: str | None = None,
    bus_name: str | None = None,
    session_bus: bool = False,
    use_bus: MessageBus | None = None,
) -> None:
    """
    Calls callback with each PropertiesChanged of the indicated path or service
    """
    await add_signal_receiver(
        callback,
        session_bus=session_bus,
        signal_name="PropertiesChanged",
        dbus_interface=PROPERTIES_INTERFACE,
        bus_name=bus_name,
        path=path,
        use_bus=use_bus,
        preserve=use_bus is not None,
    )


class DbusPropertyBlock(widget.GenPollText):
    """
    GenPollText that is updated when a D-Bus property changes.

    func draws the initial state; render draws each new value of the property
    """

    def __init__(
        self,
        *,
        path: str,
        prop: str,
        render: Callable[[Any], str],
        session_bus: bool = False,
        **config: Any,
    ) -> None:
        super().__init__(**config)
        self._path = path
        self._prop = prop
        self._render = render
        self._session_bus = session_bus

    async def _config_async(self) -> None:
        await super()._config_async()
        await watch_properties(
            self._on_change,
            path=self._path,
            session_bus=self._session_bus,
            use_bus=await self._bus(),
        )

    async def _bus(self) -> MessageBus | None:
        return None

    def _on_change(self, message: Message) -> None:
        _interface, changed, _invalidated = message.body
        if self._prop in changed:
            self.update(self._render(changed[self._prop].value))


class SystemdUnitBlock(DbusPropertyBlock):
    """
    State (ActiveState) of a systemd unit.

    systemd only issues unit changes to subscribed clients, so it uses a
    own bus with Subscribe and closes it when finished
    """

    def __init__(self, *, unit_path: str, **config: Any) -> None:
        super().__init__(path=unit_path, prop="ActiveState", **config)
        self._own_bus: MessageBus | None = None

    async def _bus(self) -> MessageBus:
        self._own_bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        await self._own_bus.call(
            Message(
                destination="org.freedesktop.systemd1",
                path="/org/freedesktop/systemd1",
                interface="org.freedesktop.systemd1.Manager",
                member="Subscribe",
            )
        )
        return self._own_bus

    def finalize(self) -> None:
        if self._own_bus is not None:
            self._own_bus.disconnect()
        super().finalize()
