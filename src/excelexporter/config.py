import logging
import toml
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


builtin_kws = [
    "tr",
    "Label/text",
    "Label/tooltip_text",
    "Button/text",
    "Button/tooltip_text",
    "TextEdit/text",
    "TextEdit/tooltip_text",
    "TextEdit/placeholder_text",
    "TextEdit/tooltip_text",
    "LineEdit/text",
    "LineEdit/tooltip_text",
    "LineEdit/placeholder_text",
    "RichTextLabel/text"
    "RichTextLabel/tooltip_text"
]


@dataclass
class Localization:
    babel_keywords: list = field(
        default_factory=lambda: builtin_kws)
    pot_file: str = "lang/template.pot"


@dataclass
class Configuration:
    ignore_sheet_mark: str = field(default="~")
    ignore_field_mark: str = field(default="*")
    custom_generator: str = field(default="GDS2.0")
    input: str = field(default="data")
    output: str = field(default="dist")
    project_root: str = field(default="../")
    localization: Localization = field(default_factory=Localization)

    @classmethod
    def load(cls, filename: str = "export.toml") -> 'Configuration':
        with open(filename) as f:
            data = toml.load(f)
            config = Configuration(**data)
            return config

    def save(self, filename: str = "export.toml"):
        with open(filename, "w") as f:
            data = asdict(self)
            toml.dump(data, f)
