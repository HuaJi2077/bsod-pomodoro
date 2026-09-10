# -*- coding: utf-8 -*-
"""帮助与关于：菜单触发的简介弹窗、超链接跳转默认浏览器。

- pomodoro（帮助）：番茄钟简介弹窗；
- info（关于）：软件简介弹窗，含超链接，点击后由系统默认浏览器打开；
- update（检查更新）：不弹窗，直接跳转默认浏览器。
"""

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtGui import QDesktopServices

from utils.dialog import show_rich_dialog

# 项目主页与更新页（检查更新跳转 Releases 页面）
URL_HOME = "https://github.com/HuaJi2077/bsod-pomodoro"
URL_UPDATE = "https://github.com/HuaJi2077/bsod-pomodoro/releases"



def show_pomodoro_help(parent=None) -> None:
    """帮助菜单：番茄钟简介弹窗。"""
    show_rich_dialog(QCoreApplication.translate("Help", "番茄钟简介"), QCoreApplication.translate("Help",
        "<h3>什么是番茄工作法？</h3>"
        "<p>把任务拆分成一个个专注的「番茄钟」：工作一段时间后短暂休息，"
        "劳逸结合，保持节奏。</p>"
        "<p>一轮循环：<b>工作若干次 → 短休息若干次 → 长休息一次 → 下一轮循环</b>；"
        "这样的一轮完整周期称为<b>一个番茄</b>。</p>"), parent)


def show_about(parent=None) -> None:
    """关于菜单：软件简介弹窗，超链接点击后用默认浏览器打开。"""
    show_rich_dialog(
        QCoreApplication.translate("Help", "关于"),
        QCoreApplication.translate("Help", "<h3>蓝屏番茄钟</h3>") +
        QCoreApplication.translate("Help",
            "<p>一款会「伪装蓝屏」的番茄钟：休息时既能伪装成蓝屏死机、彩虹猫病毒，"
            "也支持正常提醒，让你休息的名正言顺，不再被老板诟病。</p>") +
        QCoreApplication.translate("Help", "<p>本项目开源且免费，详细信息查看仓库</p>") +
        QCoreApplication.translate("Help", "<p>GitHub 仓库：<a href='{url}'>{url}</a></p>").format(url=URL_HOME),
        parent)


def open_update_page() -> None:
    """更新菜单：直接用系统默认浏览器打开更新页。"""
    QDesktopServices.openUrl(QUrl(URL_UPDATE))
