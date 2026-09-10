# -*- coding: utf-8 -*-
"""番茄钟主逻辑：预设数据加载、界面配置读取、状态栏信息与休息提醒。

预设数据由根目录 presets.json 数据驱动，时长一律以秒存储
（界面 QTimeEdit 支持时:分:秒，加载走 utils 的 JSON 工具，兼容打包），
自定义模式下每改一步数值都会即时写回 JSON；
计时调度与屏保线程全部委托给 services 层，本层只做交互控制与状态维护。
休息提醒按屏保选项分流：蓝屏死机 / 彩虹猫为全屏屏保，普通提示为模态置顶弹窗。
"""

from PySide6.QtCore import QCoreApplication, Qt, QTime
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from services import HardcoreService, PomodoroService, ScreensaverService
from services.pomodoro_service import PHASE_LONG_REST, PHASE_SHORT_REST, PHASE_WORK
from services.screensaver import KIND_BSOD, KIND_NYANCAT
from utils.dialog import DialogType, show_dialog
from utils.json_config import load_json, save_json

from .base import BasePageLogic


def phase_label(key: str) -> str:
    """阶段 key -> 显示文本（运行时查翻译表，语言切换后立即生效）。"""
    if key == PHASE_WORK:
        return QCoreApplication.translate("PomodoroLogic", "工作")
    if key == PHASE_SHORT_REST:
        return QCoreApplication.translate("PomodoroLogic", "短休息")
    return QCoreApplication.translate("PomodoroLogic", "长休息")

# 预设配置文件（相对项目根目录，路径由 utils 工具定位，兼容 PyInstaller 打包）
PRESETS_FILE = "data/presets.json"
# JSON 缺失或损坏时自定义模式的兜底数值（时长单位：秒）
_CUSTOM_DEFAULTS = {"work": 1500, "short_rest": 300, "long_rest": 900,
                     "short_count": 3, "loops": 1}
# 休息屏保选项：0 蓝屏死机 / 1 彩虹猫 / 2 普通提示
SCREENSAVER_NORMAL = 2


def format_seconds(seconds: int) -> str:
    """把秒数格式化为 mm:ss。"""
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def time_edit_seconds(time_edit) -> int:
    """读取 QTimeEdit 当前值并折算为总秒数。"""
    t = time_edit.time()
    return t.hour() * 3600 + t.minute() * 60 + t.second()


def seconds_to_qtime(seconds: int) -> QTime:
    """把总秒数折算为 QTime（时:分:秒），用于填充 QTimeEdit。"""
    return QTime(seconds // 3600, seconds % 3600 // 60, seconds % 60)


class RestDialog(QDialog):
    """休息提醒弹窗（屏保占位）：模态、置顶、可关闭，实时显示剩余休息时间。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("休息提醒"))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setModal(True)  # 模态：休息期间主窗口不可操作；弹窗本身可随时关闭
        self.setMinimumSize(380, 240)

        self.label_title = QLabel(self.tr("你该休息了"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.label_title.setStyleSheet("font: 700 22pt 'Microsoft YaHei UI';")

        self.label_phase = QLabel(self.tr("休息类型：短休息"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.label_phase.setStyleSheet("font: 14pt 'Microsoft YaHei UI';")

        self.label_total = QLabel(self.tr("本次休息时长：00:00"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.label_total.setStyleSheet("font: 14pt 'Microsoft YaHei UI';")

        self.label_time = QLabel(self.tr("剩余 00:00"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.label_time.setStyleSheet("font: 700 32pt 'Microsoft YaHei UI';")

        self.label_tip = QLabel(self.tr("休息结束后自动关闭该窗口，也可以手动关闭本窗口"), alignment=Qt.AlignmentFlag.AlignCenter)
        self.label_tip.setStyleSheet("color: gray;")

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.label_title)
        layout.addWidget(self.label_phase)
        layout.addWidget(self.label_total)
        layout.addWidget(self.label_time)
        layout.addStretch()
        layout.addWidget(self.label_tip)

    def update_info(self, phase: str, total: int, remaining: int) -> None:
        """刷新休息类型、总时长与剩余时间（phase 传显示文本）。"""
        self.label_phase.setText(self.tr("休息类型：") + phase)
        self.label_total.setText(self.tr("本次休息时长：") + format_seconds(total))
        self.label_time.setText(self.tr("剩余 ") + format_seconds(remaining))


class PomodoroLogic(BasePageLogic):
    """番茄钟页面逻辑：交互控制、状态维护、状态栏信息展示。"""

    def __init__(self, ui):
        # 预设数据：从 JSON 加载（数据驱动），须早于基类的 _setup_ui
        config = load_json(PRESETS_FILE, default={})
        self._modes = config.get("modes", [])
        self._custom = {**_CUSTOM_DEFAULTS, **(config.get("custom") or {})}
        self._loading = False  # 程序填充数值期间不触发保存
        super().__init__(ui)  # 依次执行 _setup_ui / _bind_events
        self._service = PomodoroService()
        self._screensaver = ScreensaverService()
        self._hardcore = HardcoreService()
        self._rest_dialog = None
        self._notifier = None  # 系统通知回调（由外部注入，如托盘气泡）
        # 当前阶段信息，用于组装状态栏文本
        self._phase_name = ""
        self._phase_duration = 0
        self._seg_cur = 0
        self._seg_total = 0
        self._loop_cur = 0
        self._loop_total = 0
        self._connect_service_signals()

    # ---------- 初始化 ----------

    def _setup_ui(self) -> None:
        """初始化默认预设与按钮初始状态（时长可精确到秒，00:00:00 即立即休息）。"""
        ui = self.ui
        # 默认选中"标准番茄钟"并应用预设
        ui.comboBox_pomodoro.setCurrentIndex(0)
        self._apply_mode(0)

        ui.pushButton_stop.setEnabled(False)
        ui.pushButton_pause.setEnabled(False)
        ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "就绪：配置完成后点击“开始”"))

    def refresh_statusbar(self) -> None:
        """语言切换后重发当前状态文本（状态栏消息不会随翻译器自动重译）。"""
        if self._service is not None and self._service.running:
            self._update_statusbar(self._service._remaining)
        else:
            self.ui.statusbar.showMessage(
                QCoreApplication.translate("PomodoroLogic", "就绪：配置完成后点击“开始”"))

    def _bind_events(self) -> None:
        """绑定页面控件事件。"""
        ui = self.ui
        ui.comboBox_pomodoro.currentIndexChanged.connect(self._on_mode_changed)
        ui.pushButton_start.clicked.connect(self._on_start)
        ui.pushButton_stop.clicked.connect(self._on_stop)
        ui.pushButton_pause.clicked.connect(self._on_pause_toggled)
        ui.checkBox_hardMode.toggled.connect(self._on_hard_mode_toggled)
        # 数值变化：自定义模式下即时写回 JSON（QTimeEdit 与 QSpinBox 信号不同）
        for editor in (ui.timeEdit_workTime, ui.timeEdit_shortRestTime, ui.timeEdit_longRestTime):
            editor.timeChanged.connect(self._on_value_changed)
        for spin in (ui.spinBox_shortRestConut, ui.spinBox_loopCount):
            spin.valueChanged.connect(self._on_value_changed)

    def _on_hard_mode_toggled(self, checked: bool) -> None:
        """切换硬核模式：开启时弹出警告，告知休息期间键鼠将被禁用。"""
        if not checked:
            self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "硬核模式已关闭"))
            return
        self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "硬核模式已开启：休息期间将禁用键盘和鼠标"))
        show_dialog(
            DialogType.WARNING,
            QCoreApplication.translate("PomodoroLogic", "硬核模式警告"),
            QCoreApplication.translate(
                "PomodoroLogic",
                "硬核模式已开启！\n\n番茄钟运行期间，一旦进入休息阶段，"
                "键盘和鼠标都会被锁定，直到休息结束才能恢复。\n\n"
                "通过 Ctrl+Alt+Del 唤出系统界面进行自救。"),
            parent=self.ui.centralwidget,
        )

    def _connect_service_signals(self) -> None:
        """连接服务层信号：阶段变化 / 秒级进度 / 结束事件均回传主线程处理。"""
        self._service.phase_changed.connect(self._on_phase_changed)
        self._service.tick.connect(self._on_tick)
        self._service.phase_finished.connect(self._on_phase_finished)
        self._service.all_finished.connect(self._on_all_finished)
        self._service.error.connect(self._on_error)

    def shutdown(self) -> None:
        """应用退出兜底：停表、关休息提醒，确保硬核锁定被解除。"""
        self._service.stop()
        self._close_rest_dialog()

    def set_notifier(self, notifier) -> None:
        """注入系统通知回调（形如 notify(title, text)），用于休息提醒。"""
        self._notifier = notifier

    # ---------- 交互事件 ----------

    def _on_mode_changed(self, index: int) -> None:
        """切换模式：填充数值，"自定义"模式下才开放数值编辑。"""
        self._apply_mode(index)
        if self._is_custom_mode():
            self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "自定义模式：可自由调整各项数值，改动即时保存"))
        else:
            self.ui.statusbar.showMessage(
                QCoreApplication.translate("PomodoroLogic", "已应用预设：")
                + self.ui.comboBox_pomodoro.currentText())

    def _on_value_changed(self) -> None:
        """数值变化：自定义模式下每改一步就写回 JSON，实现即时保存（时长存秒）。"""
        if self._loading or not self._is_custom_mode():
            return
        ui = self.ui
        self._custom = {
            "work": time_edit_seconds(ui.timeEdit_workTime),
            "short_rest": time_edit_seconds(ui.timeEdit_shortRestTime),
            "long_rest": time_edit_seconds(ui.timeEdit_longRestTime),
            "short_count": ui.spinBox_shortRestConut.value(),
            "loops": ui.spinBox_loopCount.value(),
        }
        save_json(PRESETS_FILE, {"modes": self._modes, "custom": self._custom})

    def _on_start(self) -> None:
        """点击开始：读取配置（时长折算为秒）并启动服务，锁定界面设置。"""
        ui = self.ui
        self._service.start(
            time_edit_seconds(ui.timeEdit_workTime),
            time_edit_seconds(ui.timeEdit_shortRestTime),
            time_edit_seconds(ui.timeEdit_longRestTime),
            ui.spinBox_shortRestConut.value(),
            ui.spinBox_loopCount.value(),
        )
        if not self._service.running:
            return  # 配置无效，错误信息已由 error 信号提示

        self._set_settings_enabled(False)
        ui.pushButton_start.setEnabled(False)
        ui.pushButton_stop.setEnabled(True)
        ui.pushButton_pause.setEnabled(True)
        ui.pushButton_pause.setText(QCoreApplication.translate("PomodoroLogic", "暂停"))

    def _on_pause_toggled(self) -> None:
        """点击暂停/继续：切换服务状态并同步按钮文案。"""
        if self._service.paused:
            self._service.resume()
            self.ui.pushButton_pause.setText(QCoreApplication.translate("PomodoroLogic", "暂停"))
            self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "已继续"))
        else:
            self._service.pause()
            self.ui.pushButton_pause.setText(QCoreApplication.translate("PomodoroLogic", "继续"))
            self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "已暂停"))

    def _on_stop(self) -> None:
        """点击停止：确认后终止计时并恢复初始状态。"""
        if not show_dialog(
            DialogType.QUESTION,
            QCoreApplication.translate("PomodoroLogic", "停止确认"),
            QCoreApplication.translate("PomodoroLogic", "确定要停止番茄钟吗？当前进度将会丢失。"),
            parent=self.ui.centralwidget,
        ):
            return

        self._service.stop()
        self._close_rest_dialog()
        self._reset_controls()
        self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "已停止，番茄钟已重置"))

    # ---------- 服务信号处理 ----------

    def _on_phase_changed(self, name: str, duration: int, seg_cur: int,
                          seg_total: int, loop_cur: int, loop_total: int) -> None:
        """进入新阶段：更新进度信息；休息阶段按屏保选项弹出提醒。"""
        self._phase_name = name
        self._phase_duration = duration
        self._seg_cur = seg_cur
        self._seg_total = seg_total
        self._loop_cur = loop_cur
        self._loop_total = loop_total
        self._update_statusbar(duration)

        if name in (PHASE_SHORT_REST, PHASE_LONG_REST):
            self._open_rest_dialog(name, duration)
        else:
            self._close_rest_dialog()

    def _on_tick(self, remaining: int) -> None:
        """秒级进度：刷新状态栏与休息弹窗的剩余时间。"""
        self._update_statusbar(remaining)
        if self._rest_dialog is not None and self._rest_dialog.isVisible():
            self._rest_dialog.update_info(phase_label(self._phase_name),
                                          self._phase_duration, remaining)

    def _on_phase_finished(self, name: str) -> None:
        """阶段结束：在状态栏给出简短反馈（随后会被新阶段信息覆盖）。"""
        if name == PHASE_WORK:
            self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "本段工作完成，进入休息"))
        else:
            self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "休息结束，继续工作"))

    def _on_all_finished(self) -> None:
        """全部循环结束：恢复控件并给出友好提示。"""
        self._close_rest_dialog()
        self._reset_controls()
        self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "全部循环完成，干得漂亮！"))
        show_dialog(
            DialogType.INFO,
            QCoreApplication.translate("PomodoroLogic", "完成"),
            QCoreApplication.translate("PomodoroLogic", "全部番茄钟循环已完成，放松一下眼睛吧！"),
            parent=self.ui.centralwidget,
        )

    def _on_error(self, message: str) -> None:
        """服务层报错：状态栏提示，不弹窗打断用户。"""
        self.ui.statusbar.showMessage(QCoreApplication.translate("PomodoroLogic", "出错了：") + message)

    # ---------- 内部工具 ----------

    def _is_custom_mode(self) -> bool:
        """当前是否为"自定义"模式（预设列表之外的索引，即界面最后一项）。"""
        return self.ui.comboBox_pomodoro.currentIndex() >= len(self._modes)

    def _apply_mode(self, index: int) -> None:
        """按模式索引填充数值：预设取自 JSON，自定义取上次保存值（时长均为秒）。"""
        ui = self.ui
        values = self._modes[index] if index < len(self._modes) else self._custom
        self._loading = True  # 程序填充数值期间不触发保存
        ui.timeEdit_workTime.setTime(seconds_to_qtime(values.get("work", 1500)))
        ui.timeEdit_shortRestTime.setTime(seconds_to_qtime(values.get("short_rest", 300)))
        ui.timeEdit_longRestTime.setTime(seconds_to_qtime(values.get("long_rest", 900)))
        ui.spinBox_shortRestConut.setValue(values.get("short_count", 3))
        ui.spinBox_loopCount.setValue(values.get("loops", 1))
        self._loading = False

        editable = self._is_custom_mode()
        for editor in (ui.timeEdit_workTime, ui.timeEdit_shortRestTime, ui.timeEdit_longRestTime,
                       ui.spinBox_shortRestConut):
            editor.setEnabled(editable)
        # 番茄个数不随预设锁定，任何模式下都可自由调整（运行期间才统一锁定）
        ui.spinBox_loopCount.setEnabled(True)

    def _set_settings_enabled(self, enabled: bool) -> None:
        """运行期间锁定全部设置控件，停止后恢复。"""
        ui = self.ui
        ui.comboBox_pomodoro.setEnabled(enabled)
        ui.comboBox_screensaver.setEnabled(enabled)
        ui.checkBox_hardMode.setEnabled(enabled)
        # 其余数值项仅在"自定义"模式下可编辑，预设模式保持只读
        editable = enabled and self._is_custom_mode()
        for editor in (ui.timeEdit_workTime, ui.timeEdit_shortRestTime, ui.timeEdit_longRestTime,
                       ui.spinBox_shortRestConut):
            editor.setEnabled(editable)
        # 番茄个数除运行期间外始终可改，此处不按预设锁定
        ui.spinBox_loopCount.setEnabled(enabled)

    def _reset_controls(self) -> None:
        """恢复到待机状态的按钮与设置可用性。"""
        ui = self.ui
        ui.pushButton_start.setEnabled(True)
        ui.pushButton_stop.setEnabled(False)
        ui.pushButton_pause.setEnabled(False)
        ui.pushButton_pause.setText(QCoreApplication.translate("PomodoroLogic", "暂停"))
        self._set_settings_enabled(True)

    def _update_statusbar(self, remaining: int) -> None:
        """组装状态栏文本：阶段 + 剩余时间 + 阶段 + 个番茄。"""
        text = (QCoreApplication.translate("PomodoroLogic", "当前状态：") + phase_label(self._phase_name)
                + QCoreApplication.translate("PomodoroLogic", " ｜ 剩余时间： ") + format_seconds(remaining)
                + QCoreApplication.translate("PomodoroLogic", " ｜ 第 ") + f"{self._seg_cur}/{self._seg_total}"
                + QCoreApplication.translate("PomodoroLogic", " 阶段")
                + QCoreApplication.translate("PomodoroLogic", " ｜ 第 ") + f"{self._loop_cur}/{self._loop_total}"
                + QCoreApplication.translate("PomodoroLogic", " 个番茄"))
        self.ui.statusbar.showMessage(text)

    def _open_rest_dialog(self, phase: str, duration: int) -> None:
        """按屏保选项分流休息提醒：蓝屏 / 彩虹猫走全屏屏保，普通提示走弹窗。

        硬核模式开启时，休息开始即锁定键鼠。
        """
        if self.ui.checkBox_hardMode.isChecked():
            self._hardcore.lock()
        screensaver = self.ui.comboBox_screensaver.currentIndex()
        if screensaver == KIND_BSOD:
            self._screensaver.show(KIND_BSOD)
        elif screensaver == KIND_NYANCAT:
            self._screensaver.show(KIND_NYANCAT)
        elif screensaver == SCREENSAVER_NORMAL:
            # 普通提示：模态弹窗 + 系统通知（窗口在前台或托盘化均发送）
            if self._notifier is not None:
                self._notifier(
                    QCoreApplication.translate("PomodoroLogic", "休息提醒"),
                    QCoreApplication.translate("PomodoroLogic", "你该休息了！")
                    + f" {phase_label(phase)} {format_seconds(duration)}")
            if self._rest_dialog is None:
                self._rest_dialog = RestDialog(self.ui.centralwidget)
            self._rest_dialog.update_info(phase_label(phase), duration, duration)
            self._rest_dialog.show()
            self._rest_dialog.raise_()

    def _close_rest_dialog(self) -> None:
        """关闭休息提醒：屏保、弹窗统一回收，硬核锁定的键鼠一并解除。"""
        self._hardcore.unlock()
        self._screensaver.close()
        if self._rest_dialog is not None:
            self._rest_dialog.close()
            self._rest_dialog.deleteLater()
            self._rest_dialog = None
