# -*- coding: utf-8 -*-
"""页面业务逻辑包。

将 UI 控件的事件处理从主窗口中解耦出来：
每个子模块负责一块独立功能（番茄钟 / 托盘等），
通过注入的 ui 引用操作界面，在 main.py 中装配。
"""

from .base import BasePageLogic
from .pomodoro import PomodoroLogic
from .tray import TrayController

__all__ = ["BasePageLogic", "PomodoroLogic", "TrayController"]
