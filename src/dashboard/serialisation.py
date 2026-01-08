import base64
import json
import zlib
from typing import Any

from logging_setup import get_logger

logger = get_logger(__name__)


def encode_state(state: dict[str, Any]) -> str:
    """Compress and encode a dictionary into a URL-safe string."""
    json_str = json.dumps(state)
    compressed = zlib.compress(json_str.encode("utf-8"))
    base64_bytes = base64.urlsafe_b64encode(compressed)
    return base64_bytes.decode("ascii")


def decode_state(encoded_str: str) -> dict[str, Any]:
    """Decode and decompress a string back into a dictionary."""
    try:
        base64_bytes = encoded_str.encode("ascii")
        compressed = base64.urlsafe_b64decode(base64_bytes)
        json_str = zlib.decompress(compressed).decode("utf-8")
        return json.loads(json_str)
    except Exception:
        logger.exception("Decoding error")
        return {}
