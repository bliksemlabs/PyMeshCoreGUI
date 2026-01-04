from datetime import datetime
from typing import Any


class Message:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload

    @property
    def timestamp(self) -> datetime | None:
        ts = self.payload.get("sender_timestamp")
        return datetime.fromtimestamp(ts) if ts else None

    @property
    def text(self) -> str:
        return self.payload.get("text", "")

    def formatted(self) -> str:
        if self.timestamp:
            time_str = self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return f"[{time_str}] {self.text}"
        return self.text
