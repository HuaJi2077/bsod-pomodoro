# -*- coding: utf-8 -*-
"""JSON 配置读写工具：兼容开发与 PyInstaller 打包环境。

- 读取：优先读可写数据目录（打包后为 exe 所在目录），不存在再回退
  resource_path 指向的内置资源（开发环境为项目根目录，打包后为解压临时目录）；
- 写入：始终写可写数据目录，保证用户改动在打包版中也能持久保存。
"""

import json
import sys
from pathlib import Path
from typing import Any

from . import resource_path


def _writable_root() -> Path:
    """返回可写的数据根目录。

    开发环境为项目根目录；PyInstaller 打包后为 exe 所在目录
    （resource_path 指向的 _MEIPASS 是临时解压目录，退出即销毁，不能存用户数据）。
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def load_json(relative_path: str, default: Any = None) -> Any:
    """读取 JSON 文件并返回解析结果。

    优先读可写数据目录（用户改动），不存在再读内置资源（默认值）；
    两者都不可用时返回 default，调用方无需额外处理异常。

    Args:
        relative_path: 相对数据根目录的文件路径。
        default: 读取失败时的返回值。
    """
    for path in (_writable_root() / relative_path, resource_path(relative_path)):
        if path == _writable_root() / relative_path and not path.exists():
            continue  # 用户改动文件不存在，继续尝试内置资源
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
    return default


def save_json(relative_path: str, data: Any) -> None:
    """把 data 以缩进格式写入可写数据目录下的 JSON 文件（覆盖写入）。

    Args:
        relative_path: 相对数据根目录的文件路径。
        data: 任意可被 json 序列化的数据。
    """
    path = _writable_root() / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
