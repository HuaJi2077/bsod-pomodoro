# -*- coding: utf-8 -*-
"""屏保服务层：休息期屏保的启动与关闭调度。

蓝屏死机 / 彩虹猫屏保均为独立 QThread（各自封装在 module/ 中），
本服务负责创建线程、启动渲染与停止回收，logic 层只通过
show / close 与其交互，不触碰线程细节。
"""

from PySide6.QtCore import QObject

from module.blue_screen import BsodScreenSaver
from module.nyan_cat import NyanCatScreenSaver

# 屏保种类，与界面 comboBox_screensaver 的前两个选项对应
KIND_BSOD = 0    # 蓝屏死机
KIND_NYANCAT = 1  # 彩虹猫


class ScreensaverService(QObject):
    """屏保调度服务：同一时刻至多运行一个屏保线程。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._saver = None

    # ---------- 对外接口 ----------

    def show(self, kind: int) -> None:
        """启动指定种类的全屏屏保；已有屏保在运行时先关闭再切换。"""
        self.close()
        if kind == KIND_BSOD:
            self._saver = BsodScreenSaver()
        elif kind == KIND_NYANCAT:
            self._saver = NyanCatScreenSaver()
        else:
            return
        self._saver.start()

    def close(self) -> None:
        """停止并回收当前屏保线程（无屏保时为空操作）。"""
        if self._saver is None:
            return
        self._saver.stop()
        self._saver.wait()
        self._saver.deleteLater()
        self._saver = None

    @property
    def running(self) -> bool:
        return self._saver is not None
