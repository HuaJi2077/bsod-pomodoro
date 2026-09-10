# -*- coding: utf-8 -*-
"""彩虹猫屏保：全屏 Nyan Cat 动画，运行在独立 QThread 中。

渲染对象（Nyancat / Rainbow / StarManager）均来自原仓库
borealkiss/nyancat.py（Apache License 2.0, Copyright 2012 Hajime Hikida），
本模块仅将其组织为全屏屏保线程：start() 开始播放，stop() 结束退出。
"""

from os import environ

environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")  # 屏蔽 pygame 启动横幅

from PySide6.QtCore import QThread
import pygame

from utils.win32 import bring_to_foreground

from .nyancat import Nyancat
from .rainbow import Rainbow
from .star_manager import StarManager

FPS = 12                                  # 原实现的动画帧率
BACKGROUND_COLOR = pygame.Color(15, 77, 143)
NUM_STARS = 20                            # 同屏星星数量
STAR_VELOCITY_X = -5                      # 星星水平速度


class NyanCatScreenSaver(QThread):
    """彩虹猫屏保线程：start() 显示全屏动画，stop() 结束并退出。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop_flag = False

    def stop(self) -> None:
        """请求结束屏保（线程安全，由外部线程调用）。"""
        self._stop_flag = True

    def run(self) -> None:
        pygame.init()
        try:
            pygame.mouse.set_visible(False)
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            screen_rect = screen.get_rect()

            # 猫按屏幕高度的 1/3 显示（Nyancat 内部会保持 35:25 的宽高比）
            cat = Nyancat(pygame.Rect(0, 0, screen_rect.height // 3, screen_rect.height // 3))
            cat.rect.center = screen_rect.center
            rainbow = Rainbow(cat.rect, cat.cellSize)
            star_manager = StarManager(screen_rect, cat.cellSize, NUM_STARS, STAR_VELOCITY_X)

            # 主窗口托盘化时进程在后台，强制把屏保置顶并激活到前台
            bring_to_foreground(pygame.display.get_wm_info().get("window", 0))

            clock = pygame.time.Clock()
            while not self._stop_flag:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._stop_flag = True

                screen.fill(BACKGROUND_COLOR)
                rainbow.draw(screen)
                cat.draw(screen)
                star_manager.draw(screen)

                rainbow.update()
                cat.update()
                star_manager.update()

                pygame.display.flip()
                clock.tick(FPS)
        finally:
            pygame.quit()
