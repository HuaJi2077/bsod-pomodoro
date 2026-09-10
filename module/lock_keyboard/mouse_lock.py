# -*- coding: utf-8 -*-
"""鼠标锁定实现：把光标限制在屏幕左上角 1x1 像素区域内。

与 keyboard_lock 配套，供硬核模式锁定键鼠使用。
仅支持 Windows（Win32 API ClipCursor）。
"""

import ctypes
from ctypes import wintypes


def clip_cursor() -> None:
    """把光标活动范围限制在屏幕左上角 1x1 像素区域内。"""
    rect = wintypes.RECT(0, 0, 1, 1)
    ctypes.windll.user32.ClipCursor(ctypes.byref(rect))


def unclip_cursor() -> None:
    """解除光标区域限制，恢复自由移动。"""
    ctypes.windll.user32.ClipCursor(None)
