# path: pytuin_desktop/enums.py
"""Enums for typed properties."""
from __future__ import annotations
from enum import Enum

class TextAlignment(str, Enum):
    left = "left"; center = "center"; right = "right"; justify = "justify"

class ColorToken(str, Enum):
    default="default"; muted="muted"; accent="accent"; primary="primary"; secondary="secondary"
    success="success"; warning="warning"; danger="danger"; info="info"
