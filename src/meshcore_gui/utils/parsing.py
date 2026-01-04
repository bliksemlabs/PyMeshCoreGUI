import logging
from typing import Any

_LOGGER = logging.getLogger(__name__)


def parse_rx_log_data(payload: Any) -> dict[str, Any]:
    """Parse RX_LOG event payload to extract LoRa packet details.

    Expected format (hex):
      byte0: header
      byte1: path_len
      next path_len bytes: path nodes
      next byte: channel_hash (optional)
    """
    result: dict[str, Any] = {}

    try:
        hex_str = None

        if isinstance(payload, dict):
            hex_str = payload.get("payload") or payload.get("raw_hex")
        elif isinstance(payload, (str, bytes)):
            hex_str = payload

        if not hex_str:
            return result

        if isinstance(hex_str, bytes):
            hex_str = hex_str.hex()

        hex_str = (
            str(hex_str).lower().replace(" ", "").replace("\n", "").replace("\r", "")
        )

        if len(hex_str) < 4:
            return result

        result["header"] = hex_str[0:2]

        try:
            path_len = int(hex_str[2:4], 16)
            result["path_len"] = path_len
        except ValueError:
            return {}

        path_start = 4
        path_end = path_start + (path_len * 2)

        if len(hex_str) < path_end:
            return {}

        path_hex = hex_str[path_start:path_end]
        result["path"] = path_hex
        result["path_nodes"] = [path_hex[i : i + 2] for i in range(0, len(path_hex), 2)]

        if len(hex_str) >= path_end + 2:
            result["channel_hash"] = hex_str[path_end : path_end + 2]

    except Exception as ex:
        _LOGGER.debug(f"Error parsing RX_LOG data: {ex}")

    return result
