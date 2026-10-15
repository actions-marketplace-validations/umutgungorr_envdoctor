"""Python version compatibility helpers for EnvDoctor."""

from __future__ import annotations

import sys
from dataclasses import dataclass

# Python 3.9 compatibility: slots=True was introduced in Python 3.10
_DATACLASS_KWARGS = {"slots": True} if sys.version_info >= (3, 10) else {}


def slotted_dataclass(cls=None, **kwargs):
    """Dataclass decorator that safely enables slots=True on Python >= 3.10."""
    merged = dict(_DATACLASS_KWARGS)
    merged.update(kwargs)
    if sys.version_info < (3, 10):
        merged.pop("slots", None)
    if cls is not None:
        return dataclass(**merged)(cls)
    return dataclass(**merged)
