# -*- coding: utf-8 -*-
"""页面逻辑基类，定义所有页面逻辑类的公共接口。"""

from typing import Any


class BasePageLogic:
    """页面业务逻辑基类（模板方法）。

    子类通过接收 ``ui`` 对象来访问对应页面的控件，
    并在 ``_bind_events`` 中绑定信号与槽，实现 UI 与主窗口的解耦。

    生命周期：
        __init__ -> _setup_ui -> _bind_events
        页面切换 -> on_enter（进入前台）/ on_leave（离开前台）
    """

    def __init__(self, ui: Any):
        self.ui = ui
        self._setup_ui()
        self._bind_events()

    def _setup_ui(self) -> None:
        """初始化页面专属 UI 状态，子类可按需重写。"""
        pass

    def _bind_events(self) -> None:
        """绑定页面内控件的信号与槽，子类可按需重写。"""
        pass

    def on_enter(self) -> None:
        """页面被切换到前台时调用，子类可按需重写。"""
        pass

    def on_leave(self) -> None:
        """页面离开前台时调用，子类可按需重写。"""
        pass
