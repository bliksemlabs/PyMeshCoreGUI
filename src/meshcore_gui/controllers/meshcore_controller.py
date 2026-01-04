import asyncio
from typing import Any

from PySide6.QtCore import QObject, Signal, Slot
from meshcore import MeshCore, EventType
from meshcore.events import Event

from ..utils.async_executor import AsyncExecutor
from ..utils.parsing import parse_rx_log_data


class MeshCoreController(QObject):
    self_info_ready = Signal(object)
    contacts_ready = Signal(object)
    channels_ready = Signal(object)
    event_received = Signal(object)
    message_sent = Signal(object)

    def __init__(self, mc: MeshCore, executor: AsyncExecutor):
        super().__init__()
        self.mc = mc
        self.executor = executor
        self._subscriptions = []
        self._shutdown_called = False

    @Slot(object)
    def process_event(self, event: Event):
        if event.type == EventType.RX_LOG_DATA:
            # TODO: Publish this to a dedicated debugging tab
            print("RX_LOG_DATA", parse_rx_log_data(event.payload))

        elif event.type == EventType.NO_MORE_MSGS:
            pass

    @Slot()
    def get_self_info(self):
        """Emit self_info immediately"""
        self.self_info_ready.emit(self.mc.self_info)

    @Slot()
    def fetch_contacts(self):
        """Fetch contacts async via executor"""
        self.executor.submit_async(
            self.mc.commands.get_contacts_async(), self.contacts_ready
        )

    @Slot()
    def channel_info(self):
        """Fetch contacts async via executor"""

        async def all_channels():
            for channel_idx in range(0, 40):
                await self.mc.commands.get_channel(channel_idx)

        self.executor.submit_async(all_channels(), self.channels_ready)

    @Slot()
    def send_adv(self):
        self.executor.submit_async(self.mc.commands.send_advert(True), None)

    def set_radio(self, freq: float, bw: float, sf: int, cr: int):
        self.executor.submit_async(self.mc.commands.set_radio(freq, bw, sf, cr), None)

    def reboot(self):
        self.executor.submit_async(self.mc.commands.reboot(), self.reboot)

    def set_name(self, name: str):
        self.executor.submit_async(self.mc.commands.set_name(name), None)

    def start_message_stream(self):
        """
        Subscribe to MeshCore native message events.
        Each event triggers a Qt signal to the GUI.
        """

        async def handle_message(event: Event):
            self.event_received.emit(event)

        sub1 = self.mc.subscribe(None, handle_message)

        # Keep track of subscriptions so we can unsubscribe them later
        self._subscriptions.extend([sub1])

        # Start MeshCore automatic fetching
        asyncio.run_coroutine_threadsafe(
            self.mc.start_auto_message_fetching(), self.executor.loop
        )

    @Slot(dict, str)
    def send_message(self, target: dict[str, Any], text: str):
        if "channel_idx" in target:
            self.executor.submit_async(
                self.mc.commands.send_chan_msg(target["channel_idx"], text),
                self.message_sent,
            )

        elif "public_key" in target:
            self.executor.submit_async(
                self.mc.commands.send_msg(target["public_key"], text),
                self.message_sent,
            )

    def shutdown(self):
        """Idempotent shutdown"""
        if self._shutdown_called:
            return
        self._shutdown_called = True

        # Cancel subscriptions
        for sub in self._subscriptions:
            try:
                self.mc.unsubscribe(sub)
            except Exception:
                pass
        self._subscriptions.clear()

        async def stop_fetching():
            try:
                await self.mc.stop_auto_message_fetching()
                await self.mc.disconnect()
            except Exception:
                pass

        asyncio.run_coroutine_threadsafe(stop_fetching(), self.executor.loop)

        self.executor.shutdown()
