# -*- coding: utf-8 -*-
"""业务服务层。

统一存放耗时算法、后台子线程及相关调度逻辑，
与 logic 层的页面交互逻辑分离，避免在 logic 中直接操作线程。
"""

from .hardcore import HardcoreService
from .pomodoro_service import PomodoroService
from .screensaver import ScreensaverService

__all__ = ["HardcoreService", "PomodoroService", "ScreensaverService"]
