from typing import Any


class Contact:
    """Simple container for contact payload"""

    def __init__(self, payload: dict[str, Any]):
        self.payload = payload
        self.new_message = 0

    def set_new_message(self, value: int):
        if value == 0:
            self.new_message = 0
        else:
            self.new_message += value

    @property
    def name(self) -> str:
        return self.payload.get("adv_name", "Unknown")

    @property
    def public_key(self) -> str | None:
        return self.payload.get("public_key")
