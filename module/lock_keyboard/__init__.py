# -*- coding: utf-8 -*-
"""键盘锁定包：屏蔽 / 解除屏蔽全部键盘按键与鼠标移动（硬核模式备用）。

代码抽离自开源仓库 arpy8/bsod（MIT License, Copyright 2023 Arpit Sengar），
详见本目录 LICENSE 文件。仅支持 Windows。
"""

from .keyboard_lock import block_all, unblock_all
from .mouse_lock import clip_cursor, unclip_cursor

__all__ = ["block_all", "unblock_all", "clip_cursor", "unclip_cursor"]
