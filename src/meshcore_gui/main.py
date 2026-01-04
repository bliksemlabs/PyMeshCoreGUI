import argparse
import asyncio
import signal
import sys
from meshcore import MeshCore

from PySide6.QtCore import QCoreApplication, QObject, QSettings, QThread, QTimer, Slot
from PySide6.QtWidgets import QApplication

from .controllers.channel_controller import ChannelController
from .controllers.contact_controller import ContactController
from .controllers.message_controller import MessageController
from .controllers.meshcore_controller import MeshCoreController

from .utils.async_executor import AsyncExecutor
from .views.main_window import MeshCoreWidget
from .wizard.wizard_companion import CompanionWizard


class ApplicationController(QObject):
    def __init__(self, executor, loop):
        self.mc = None
        self.meshcore_controller = None
        self.executor = executor
        self.loop = loop

    def attempt_connection(self):
        async def init_mc(port, interace_type: str):
            try:
                if interface_type == "serial":
                    mc = await MeshCore.create_serial(port)
                    return mc
                elif interface_type == "bluetooth":
                    mc = await MeshCore.create_ble(port)
                    return mc
            except:
                pass

            return None

        async def disconnect_mc(mc):
            try:
                await mc.disconnect()
            except:
                pass

        if self.mc is not None:
            future = asyncio.run_coroutine_threadsafe(disconnect_mc(self.mc), self.loop)
            self.mc = None

        port = None
        settings = QSettings()
        settings.beginGroup("interface")
        interface_type = settings.value("type", False)
        if interface_type == "serial":
            port = settings.value("port")
        elif interface_type == "bluetooth":
            port = settings.value("addr")
        settings.endGroup()

        if port is None:
            return None

        future = asyncio.run_coroutine_threadsafe(
            init_mc(port, interface_type), self.loop
        )
        self.mc = future.result()
        self.meshcore_controller = MeshCoreController(self.mc, self.executor)

        return self.mc is not None

    def start(self, force_wizard=False):
        if force_wizard:
            self.start_wizard()

        else:
            if self.mc is None:
                self.attempt_connection()

            if self.mc is not None:
                self.start_main()

            else:
                self.start_wizard()

    @Slot(bool)
    def on_wizard_done(self, success: bool):
        if success:
            self.start()

    def start_wizard(self):
        self.wizard = CompanionWizard(self)
        self.wizard.completed.connect(self.on_wizard_done)
        self.wizard.show()

    def start_main(self):
        # --- GUI ---
        self.widget = MeshCoreWidget()
        self.widget.setWindowTitle("MeshCore Chat")
        self.widget.resize(400, 600)
        self.widget.show()

        # --- Controllers ---
        self.message_controller = MessageController(self.widget.list_msgs)
        self.contact_controller = ContactController(self.widget.list_contacts)
        self.channel_controller = ChannelController(self.widget.list_channels)

        # --- Signal/Slot Connections ---
        self.meshcore_controller.event_received.connect(
            self.meshcore_controller.process_event
        )
        self.meshcore_controller.event_received.connect(
            self.message_controller.process_event
        )
        self.meshcore_controller.event_received.connect(
            self.contact_controller.process_event
        )
        self.meshcore_controller.event_received.connect(
            self.channel_controller.process_event
        )
        self.meshcore_controller.self_info_ready.connect(self.widget.update_self_info)
        self.meshcore_controller.message_sent.connect(self.widget.on_sent)

        self.contact_controller.selected.connect(self.message_controller.set_chat)
        self.contact_controller.selected.connect(self.channel_controller.deselect)
        self.contact_controller.selected.connect(self.widget.set_target)

        self.channel_controller.selected.connect(self.contact_controller.deselect)
        self.channel_controller.selected.connect(self.message_controller.set_chat)
        self.channel_controller.selected.connect(self.widget.set_target)

        self.message_controller.new_channel_message.connect(
            self.channel_controller.new_channel_message
        )
        self.message_controller.new_private_message.connect(
            self.contact_controller.new_private_message
        )

        self.widget.text_submitted.connect(self.meshcore_controller.send_message)
        self.widget.text_submitted.connect(self.message_controller.send_message)
        self.widget.button_adv.clicked.connect(self.meshcore_controller.send_adv)

        # --- Initial actions ---
        self.meshcore_controller.start_message_stream()
        self.meshcore_controller.channel_info()
        self.meshcore_controller.get_self_info()
        self.meshcore_controller.fetch_contacts()


def main():
    parser = argparse.ArgumentParser(description="MeshCore GUI")
    parser.add_argument(
        "--port", default="/dev/ttyACM0", help="Serial port for the MeshCore device"
    )
    parser.add_argument(
        "--wizard", default=False, action="store_true", help="Start the wizard"
    )
    args = parser.parse_args()

    if args.port is not None:
        settings = QSettings()
        settings.beginGroup("interface")
        settings.setValue("port", args.port)
        settings.endGroup()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    # --- asyncio loop in background thread ---
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop_thread = QThread()

    def start_loop():
        asyncio.set_event_loop(loop)
        loop.run_forever()

    loop_thread.run = start_loop
    loop_thread.start()

    executor = AsyncExecutor(loop)

    controller = ApplicationController(executor, loop)
    controller.start(args.wizard)

    # --- Idempotent shutdown ---
    shutdown_called = False

    def shutdown(*args):
        nonlocal shutdown_called
        if shutdown_called:
            return
        shutdown_called = True

        if controller.meshcore_controller:
            controller.meshcore_controller.shutdown()

        loop.call_soon_threadsafe(loop.stop)
        loop_thread.quit()
        loop_thread.wait()

        app.quit()

    # --- Signal Handlers ---
    signal.signal(signal.SIGINT, shutdown)
    app.aboutToQuit.connect(shutdown)

    # Timer to allow Python's signal handler to run
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    sys.exit(app.exec())


if __name__ == "__main__":
    QCoreApplication.setOrganizationName("Bliksem Labs B.V.")
    QCoreApplication.setOrganizationDomain("bliksemlabs.com")
    QCoreApplication.setApplicationName("MeshCoreGUI")

    main()
