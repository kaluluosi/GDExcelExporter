import logging
import toml
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class Configuration:
    ignore_sheet_mark: str = field(default="~", kw_only=True)
    ignore_field_mark: str = field(default="*", kw_only=True)
    custom_generator: str = field(default="GDS2.0", kw_only=True)
    input: str = field(default="data", kw_only=True)
    output: str = field(default="dist", kw_only=True)
    project_root: str = field(default="../", kw_only=True)

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
