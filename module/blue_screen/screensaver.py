# -*- coding: utf-8 -*-
"""蓝屏死机屏保：蓝屏图片拉伸撑满全屏，运行在独立 QThread 中。

全屏显示、蓝屏界面、隐藏鼠标指针等均为原仓库（arpy8/bsod，MIT License）的核心业务逻辑；
原仓库中的键盘 / 鼠标锁定功能已抽离到 module/lock_keyboard，本模块只负责显示。
"""

from os import environ

environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")  # 屏蔽 pygame 启动横幅

from pathlib import Path

from PySide6.QtCore import QThread
import pygame

from utils.win32 import bring_to_foreground

# 静态蓝屏画面的刷新率（帧率过高无意义，仅维持事件循环）
_FPS = 10


class BsodScreenSaver(QThread):
    """蓝屏死机屏保线程：start() 显示全屏蓝屏，stop() 结束并退出。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_flag = False

    def stop(self) -> None:
        """请求结束屏保（线程安全，由外部线程调用）。"""
        self._stop_flag = True

    def run(self) -> None:
        image_path = Path(__file__).resolve().parent / "assets" / "image.png"
        pygame.init()
        try:
            # 隐藏鼠标指针，营造系统崩溃的观感
            pygame.mouse.set_visible(False)

            # 全屏窗口：图片直接拉伸至整个屏幕（高分屏不留黑边）
            image = pygame.image.load(str(image_path))
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SWSURFACE)
            screen_size = pygame.display.get_surface().get_size()
            image = pygame.transform.smoothscale(image, screen_size)

            # 主窗口托盘化时进程在后台，强制把屏保置顶并激活到前台
            bring_to_foreground(pygame.display.get_wm_info().get("window", 0))

            clock = pygame.time.Clock()
            while not self._stop_flag:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._stop_flag = True

                screen.blit(image, (0, 0))
                pygame.display.flip()
                clock.tick(_FPS)
        finally:
            pygame.quit()
