# -*- coding: utf-8 -*-
"""托盘控制器：主窗口不真正关闭，而是隐藏到系统托盘后台运行。

- 菜单"托盘化"（action_tray）触发时隐藏窗口，程序驻留托盘；
- 点击窗口"关闭"按钮由 MainWindow.closeEvent 拦截，同样转入托盘；
- 托盘图标单击 / 双击恢复主窗口，右键菜单提供"显示主窗口 / 退出"；
- 真正退出前回调 on_quit（停表 + 解除硬核模式的键鼠锁定）。
"""

from PySide6.QtCore import QObject
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon

from utils import resource_path


class TrayController(QObject):
    """托盘控制器：hide_to_tray 转入托盘，show_window 恢复，quit_app 真正退出。"""

    def __init__(self, window, on_quit, parent=None):
        super().__init__(parent)
        self._window = window
        self._on_quit = on_quit  # 真正退出前的兜底回调（停表 / 解锁键鼠）
        self._hint_shown = False  # 转托盘的气泡提示只弹一次，避免打扰
        # 托盘 / 窗口标题（翻译后的应用名）
        app_name = self.tr("蓝屏番茄钟")

        # 托盘图标：优先用项目自带 logo，其次窗口图标，最后退回系统标准图标
        icon = QIcon(str(resource_path("icon/logo.ico")))
        if icon.isNull():
            icon = window.windowIcon()
        if icon.isNull():
            icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        window.setWindowIcon(icon)  # 窗口与托盘统一图标

        self._tray = QSystemTrayIcon(icon, self)
        self._tray.setToolTip(app_name)
        self._tray.activated.connect(self._on_activated)

        # 右键菜单：显示 / 退出
        menu = QMenu()
        menu.addAction(self.tr("显示主窗口"), self.show_window)
        menu.addAction(self.tr("退出"), self.quit_app)
        self._tray.setContextMenu(menu)

        # 菜单"托盘化"入口
        window.ui.tray.triggered.connect(self.hide_to_tray)
        self._tray.show()

    # ---------- 对外接口 ----------

    def hide_to_tray(self) -> bool:
        """隐藏主窗口并驻留托盘；系统不支持托盘时返回 False（保持原状）。"""
        if not self._tray.isSystemTrayAvailable():
            return False
        self._window.hide()
        if not self._hint_shown:
            self._tray.showMessage(
                self.tr("蓝屏番茄钟"), self.tr("程序已最小化到托盘，将在后台继续运行"),
                QSystemTrayIcon.MessageIcon.Information, 3000)
            self._hint_shown = True
        return True

    def show_window(self) -> None:
        """从托盘恢复主窗口并置前。"""
        self._window.showNormal()
        self._window.activateWindow()

    def notify(self, title: str, text: str) -> None:
        """发送系统通知（气泡 / 通知中心）；窗口是否托盘化均可发送。"""
        self._tray.showMessage(title, text,
                               QSystemTrayIcon.MessageIcon.Information, 5000)

    def quit_app(self) -> None:
        """真正退出：先执行兜底回调，再结束事件循环。"""
        self._tray.hide()
        self._on_quit()
        QApplication.quit()

    # ---------- 内部实现 ----------

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """单击 / 双击托盘图标恢复主窗口。"""
        if reason in (QSystemTrayIcon.ActivationReason.Trigger,
                      QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_window()
