from dataclasses import dataclass, field


@dataclass
class Define:
    type: list[str] = field(default_factory=list)
    desc: list[str] = field(default_factory=list)
    name: list[str] = field(default_factory=list)


@dataclass
class SheetData:
    define: Define = field(default_factory=Define)
    table: list = field(default=list)
