"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 14:53:51
Copyright © Kaluluosi All rights reserved
"""

import sys

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


def discover_generator():
    """
    发现并返回已注册导出器列表

    Returns:
        _type_: 导出器列表
    """
    generators = entry_points(group="gd_excelexporter.generator")
    return generators
