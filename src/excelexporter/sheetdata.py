from dataclasses import dataclass, field
from typing import List


@dataclass
class Define:
    type: List[str] = field(default_factory=list)
    desc: List[str] = field(default_factory=list)
    name: List[str] = field(default_factory=list)


@dataclass
class SheetData:
    define: Define = field(default_factory=Define)
    table: list = field(default=list)
