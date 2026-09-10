# -*- coding: utf-8 -*-
"""通用工具函数集合。"""

import sys
from pathlib import Path


def resource_path(relative_path: str) -> Path:
    """获取资源文件的绝对路径，兼容开发环境与 PyInstaller 打包环境。

    开发环境下以项目根目录（utils 的上级目录）为基准；
    PyInstaller 打包后，资源会被解压到临时目录 ``sys._MEIPASS`` 中。

    Args:
        relative_path: 相对于项目根目录的资源路径。

    Returns:
        资源文件的绝对路径。
    """
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path
