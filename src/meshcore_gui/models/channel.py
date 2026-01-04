from typing import Any


class Channel:
    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        self.new_message = 0

    def set_new_message(self, value: int):
        if value == 0:
            self.new_message = 0
        else:
            self.new_message += value

    @property
    def channel_idx(self) -> int | None:
        return self.payload.get("channel_idx")

    @property
    def name(self) -> str:
        return self.payload.get("channel_name", "Unnamed channel")

    @property
    def secret(self) -> bytes | None:
        return self.payload.get("channel_secret")

    def is_valid(self) -> bool:
        # Ignore channel if secret is 16 null-bytes
        return self.secret is not None and self.secret != b"\x00" * 16
