"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 14:46:38
Copyright © Kaluluosi All rights reserved
"""

import abc
from typing import Any, Dict

from gd_excelexporter.config import Configuration

Table = Dict[int, Dict[str, Any]]


class Generator(abc.ABC):
    """
    导出器基类
    """

    __extension__ = ""

    @abc.abstractmethod
    def generate(self, table: Table, config: Configuration) -> str:
        """
        导出加工逻辑

        Args:
            table (Dict[int, Dict[str, Any]]): 由Engine读取excel sheet表转换而来的字典
            config (Configuration): 配置 toml
        """
        pass

    @abc.abstractmethod
    def completed_hook(self, config: Configuration):
        """
        所有的表到处完毕后要进行的处理

        Args:
            config (Configuration): 配置 toml
        """
        pass
