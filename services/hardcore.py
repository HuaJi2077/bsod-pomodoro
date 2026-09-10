# -*- coding: utf-8 -*-
"""硬核模式服务：休息期间禁用键盘与鼠标，防止用户逃避休息。

锁定能力委托 module/lock_keyboard（键盘屏蔽 + 光标限制），
logic 层只通过 lock / unlock 与其交互。
"""

from module.lock_keyboard import block_all, clip_cursor, unblock_all, unclip_cursor


class HardcoreService:
    """硬核模式服务：lock 与 unlock 必须配对调用，否则键鼠将保持锁定。"""

    def __init__(self):
        self._locked = False

    # ---------- 对外接口 ----------

    def lock(self) -> None:
        """屏蔽全部键盘按键并限制鼠标在屏幕左上角（可重复调用，幂等）。"""
        if self._locked:
            return
        block_all()
        clip_cursor()
        self._locked = True

    def unlock(self) -> None:
        """解除键盘屏蔽与鼠标限制（未锁定时为空操作）。"""
        if not self._locked:
            return
        unblock_all()
        unclip_cursor()
        self._locked = False

    @property
    def locked(self) -> bool:
        return self._locked
