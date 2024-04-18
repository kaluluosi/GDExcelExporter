import logging
import toml
from packaging.version import Version, parse
from typing import ClassVar
from pydantic import BaseModel, ConfigDict

import gd_excelexporter

logger = logging.getLogger(__name__)


class Localization(BaseModel):
    BUILTIN_KWS: ClassVar = [
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
        "RichTextLabel/text" "RichTextLabel/tooltip_text",
    ]
    # 需要多语言提取的关键字
    babel_keywords: list = BUILTIN_KWS
    pot_file: str = "lang/template.pot"


class Configuration(BaseModel):
    version: str = ""
    engine: str = "xlrd"
    ignore_sheet_mark: str = "~"
    ignore_field_mark: str = "*"
    custom_generator: str = "GDS2.0"
    input: str = "data"
    output: str = "dist"
    project_root: str = "../"
    localization: Localization = Localization()

    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def load(cls, filename: str = "export.toml") -> "Configuration":
        """
        加载配置文件

        Args:
            filename (str, optional): 配置文件. Defaults to "export.toml".

        Returns:
            Configuration: 返回配置实例
        """
        with open(filename) as f:
            data = toml.load(f)
            config = cls(**data)

            # 检查版本更新
            old_version = Version(config.version or "0.0.0")
            cur_version = parse(gd_excelexporter.__version__)

            if old_version < cur_version:
                logger.warning(f"检测到版本更新，更新配置文件到最新版本 {cur_version}")
                config.version = gd_excelexporter.__version__
                config.save()

            return config

    def save(self, filename: str = "export.toml"):
        """
        保存配置文件

        Args:
            filename (str, optional): 配置文件. Defaults to "export.toml".
        """
        with open(filename, "w") as f:
            data = self.model_dump()
            toml.dump(data, f)
