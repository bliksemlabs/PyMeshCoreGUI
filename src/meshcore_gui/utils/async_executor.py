import asyncio
from typing import Optional, Coroutine

from PySide6.QtCore import QObject, Signal


class AsyncExecutor(QObject):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self.loop = loop

    def submit_async(self, coro: Coroutine, signal: Optional[Signal] = None):
        """Submit coroutine and emit signal on completion"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        if signal:
            future.add_done_callback(lambda f: self._emit_safe(f, signal))

    def _emit_safe(self, fut: asyncio.Future, signal: Signal):
        try:
            result = fut.result()
        except Exception as e:
            print("Async call failed:", e)
            return
        signal.emit(result)

    def shutdown(self):
        """Stop the loop safely"""
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
