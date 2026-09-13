from __future__ import annotations

from ..config import IdentifierConfig


def normalise_identifier(value: str, config: IdentifierConfig) -> str:
    result = (value or "").strip()
    if config.remove_spaces:
        result = "".join(result.split())
    for character in config.remove_characters:
        result = result.replace(character, "")
    if config.uppercase:
        result = result.upper()
    return result

