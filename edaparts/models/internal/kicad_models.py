from dataclasses import dataclass


@dataclass(frozen=True)
class KiCadPartProperty:
    value: str
    visible: bool


@dataclass(frozen=True)
class KiCadPart:
    id: int
    name: str
    symbolIdStr: str
    fields: dict[str, KiCadPartProperty]
