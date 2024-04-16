"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 14:46:38
Copyright © Kaluluosi All rights reserved
"""

import abc
import sys
from typing import Type

from gd_excelexporter.config import Configuration
from gd_excelexporter.core.models import Table

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


class Generator(abc.ABC):
    """
    导出器基类
    """

    __extension__ = ""

    @classmethod
    @abc.abstractmethod
    def generate(cls, table: Table, config: Configuration) -> str:
        """
        导出加工逻辑

        Args:
            table (Dict[int, Dict[str, Any]]): 由Engine读取excel sheet表转换而来的字典
            config (Configuration): 配置 toml
        """
        pass

    @classmethod
    @abc.abstractmethod
    def completed_hook(cls, config: Configuration):
        """
        所有的表到处完毕后要进行的处理

        Args:
            config (Configuration): 配置 toml
        """
        pass

    @classmethod
    def register_generators(cls):
        """
        发现并返回已注册导出器
        """
        generators = entry_points(group="gd_excelexporter.generator")
        return generators

    @classmethod
    def get_generator(cls, name: str) -> Type["Generator"]:
        generators = cls.register_generators()
        if name in generators.names:
            return generators[name].load()
        else:
            raise ValueError(f"Generator {name} 不存在")
