"""
author:        kaluluosi111 <kaluluosi@gmail.com>
date:          2024-04-15 14:52:20
Copyright © Kaluluosi All rights reserved
"""


# region Engine


class IllegalFile(Exception):
    """
    非法文件
    """

    def __init__(self, filename: str, *args: object) -> None:
        super().__init__(f"{filename} 不是配置表目录下的配置", *args)


class IllegalGenerator(Exception):
    """
    非法导出器
    """

    def __init__(self, name: str, *args: object) -> None:
        super().__init__(name, *args)


# endregion
