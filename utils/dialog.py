# -*- coding: utf-8 -*-
"""通用弹窗工具：统一项目中各类提示弹窗的调用方式。

调用方只需传入弹窗类型与显示内容，不直接接触 QMessageBox；
带倒计时等特殊交互的业务弹窗（如休息提醒）不在此列，由各模块自绘。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMessageBox, QWidget


class DialogType:
    """弹窗类型：决定图标与按钮组合。"""

    INFO = "info"            # 信息提示：确定
    WARNING = "warning"      # 警告提示：确定
    ERROR = "error"          # 错误提示：确定
    QUESTION = "question"    # 询问确认：是 / 否

# 各类型对应的 QMessageBox 图标
_ICONS = {
    DialogType.INFO: QMessageBox.Icon.Information,
    DialogType.WARNING: QMessageBox.Icon.Warning,
    DialogType.ERROR: QMessageBox.Icon.Critical,
    DialogType.QUESTION: QMessageBox.Icon.Question,
}


def show_dialog(kind: str, title: str, text: str,
                parent: QWidget = None) -> bool:
    """按类型弹出模态对话框并阻塞等待用户响应。

    Args:
        kind: DialogType 常量（INFO / WARNING / ERROR / QUESTION）。
        title: 弹窗标题。
        text: 弹窗正文内容。
        parent: 父窗口（可选）。

    Returns:
        QUESTION 类型返回是否点击了"是"，其余类型恒返回 True。
    """
    icon = _ICONS.get(kind, QMessageBox.Icon.Information)
    if kind == DialogType.QUESTION:
        box = QMessageBox(icon, title, text,
                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                         parent)
        box.setDefaultButton(QMessageBox.StandardButton.No)  # 默认聚焦"否"，防误触
        return box.exec() == QMessageBox.StandardButton.Yes

    box = QMessageBox(icon, title, text, QMessageBox.StandardButton.Ok, parent)
    box.exec()
    return True


def show_rich_dialog(title: str, html: str,
                      parent: QWidget = None, kind: str = DialogType.INFO) -> None:
    """弹出富文本对话框：支持 <a href> 超链接，点击后用系统默认浏览器打开。

    QMessageBox 内部标签的 openExternalLinks 默认是 False（点击链接不发任何事），
    这里手动开启，让富文本中的链接点击即跳转外部浏览器。
    """
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setIcon(_ICONS.get(kind, QMessageBox.Icon.Information))
    box.setTextFormat(Qt.TextFormat.RichText)
    box.setText(html)
    label = box.findChild(QLabel)
    if label is not None:
        label.setOpenExternalLinks(True)
    box.exec()
