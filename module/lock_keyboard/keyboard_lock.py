# -*- coding: utf-8 -*-
"""键盘按键屏蔽实现。

原逻辑来自开源仓库 arpy8/bsod（MIT License, Copyright 2023 Arpit Sengar），
为保证屏保模块职责单一而抽离至此，供硬核模式按需启用。
仅支持 Windows（keyboard 库限制）。
"""

import keyboard

# keyboard 库可屏蔽的按键码范围（原实现为 0~149）
_KEY_CODES = range(150)


def block_all() -> None:
    """屏蔽全部键盘按键（可重复调用，幂等）。"""
    for code in _KEY_CODES:
        keyboard.block_key(code)


def unblock_all() -> None:
    """解除全部键盘按键的屏蔽，与 block_all 配对使用。"""
    for code in _KEY_CODES:
        keyboard.unblock_key(code)
