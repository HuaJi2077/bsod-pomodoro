# -*- coding: utf-8 -*-
"""Windows 窗口控制工具（纯 ctypes，免依赖 pywin32）。"""

import ctypes

# SetWindowPos 的常用标志
HWND_TOPMOST = -1        # 置于所有非置顶窗口之上
SWP_NOSIZE = 0x0001      # 保持尺寸
SWP_NOMOVE = 0x0002      # 保持位置
SWP_SHOWWINDOW = 0x0040  # 显示窗口


def bring_to_foreground(window_id: int) -> None:
    """把窗口强制置顶并尝试激活到前台。

    用于托盘化（主窗口已隐藏）后弹出的全屏屏保：Windows 默认把后台进程
    创建的窗口压在下层，置顶 + 前台激活确保屏保覆盖整个屏幕。
    window_id 无效（如无窗口环境）时静默跳过。
    """
    if not window_id:
        return
    user32 = ctypes.windll.user32
    user32.SetWindowPos(window_id, HWND_TOPMOST, 0, 0, 0, 0,
                       SWP_NOSIZE | SWP_NOMOVE | SWP_SHOWWINDOW)
    user32.SetForegroundWindow(window_id)
