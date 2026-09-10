# -*- coding: utf-8 -*-
"""用户设置：主题与语言的持久化（data/settings.json）。

自定义番茄钟配置的持久化见 data/presets.json（由 PomodoroLogic 维护）。
"""

from utils.json_config import load_json, save_json

SETTINGS_FILE = "data/settings.json"

# 首次运行（无设置文件）时的默认值
DEFAULTS = {
    "theme": "light",      # 亮 / 暗主题："light" / "dark"
    "language": "zh_CN",   # 界面语言："zh_CN" / "en_US"
}


def load_settings() -> dict:
    """读取用户设置，文件缺失或字段缺失时用默认值补齐。"""
    data = load_json(SETTINGS_FILE, default=None)
    settings = dict(DEFAULTS)
    if isinstance(data, dict):
        for key, value in data.items():
            if key in DEFAULTS:
                settings[key] = value
    return settings


def save_settings(settings: dict) -> None:
    """整体写回用户设置文件。"""
    save_json(SETTINGS_FILE, settings)
