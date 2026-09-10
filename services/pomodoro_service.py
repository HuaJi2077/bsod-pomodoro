# -*- coding: utf-8 -*-
"""番茄钟服务层：阶段调度与倒计时引擎。

负责维护"工作 / 短休息 / 长休息"的阶段队列并按秒驱动倒计时，
向上层（logic/）仅暴露信号与 start / pause / resume / stop 方法，
隐藏定时器与调度细节。后续休息屏保（BSOD / 彩虹猫等）也挂在本层。
"""

from PySide6.QtCore import QObject, QTimer, Signal

# 阶段标识（稳定 key，供信号传递与比较；显示文本由 logic 层翻译）
PHASE_WORK = "work"
PHASE_SHORT_REST = "short_rest"
PHASE_LONG_REST = "long_rest"


class PomodoroService(QObject):
    """番茄钟计时引擎：构建阶段队列并逐秒倒计时，结果通过信号通知 UI 层。"""

    tick = Signal(int)  # 每秒触发，参数为当前阶段剩余秒数
    # 阶段名 / 阶段总秒数 / 段序号 / 总段数 / 轮序号 / 总轮数（序号从 1 开始）
    phase_changed = Signal(str, int, int, int, int, int)
    phase_finished = Signal(str)  # 某个阶段倒计时归零
    all_finished = Signal()       # 全部循环结束
    error = Signal(str)           # 配置或运行期错误

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_timeout)
        self._phases = []          # [(阶段名, 秒数), ...]
        self._seg_per_loop = 0     # 每轮包含的阶段数，用于计算轮进度
        self._index = 0
        self._remaining = 0
        self._running = False
        self._paused = False

    # ---------- 对外接口 ----------

    def start(self, work_sec: int, short_sec: int, long_sec: int,
              short_count: int, loops: int) -> None:
        """按配置构建阶段队列并开始倒计时（时长单位均为秒）。

        每轮结构为：(工作 + 短休息) * short_count + 工作 + 长休息，
        即 short_count 次短休后进入长休息，整个结构重复 loops 轮。
        工作时间允许为 0 秒：0 秒的工作阶段不会入队，点击开始后立即进入休息，
        休息结束后无缝衔接下一个休息阶段（整蛊模式）。
        """
        if self._running:
            self.error.emit(self.tr("番茄钟已在运行中"))
            return
        if work_sec < 0 or min(short_sec, long_sec, short_count, loops) < 1:
            self.error.emit(self.tr("配置无效：除工作时间外，所有数值都必须大于 0"))
            return

        self._phases, self._seg_per_loop = self._build_phases(
            work_sec, short_sec, long_sec, short_count, loops)
        self._index = 0
        self._remaining = self._phases[0][1]
        self._running = True
        self._paused = False
        self._emit_phase_changed()
        self._timer.start()

    def pause(self) -> None:
        """暂停倒计时（保留进度）。"""
        if self._running and not self._paused:
            self._paused = True
            self._timer.stop()

    def resume(self) -> None:
        """从暂停处继续倒计时。"""
        if self._running and self._paused:
            self._paused = False
            self._timer.start()

    def stop(self) -> None:
        """停止计时并清空全部进度。"""
        self._timer.stop()
        self._phases = []
        self._seg_per_loop = 0
        self._index = 0
        self._remaining = 0
        self._running = False
        self._paused = False

    @property
    def running(self) -> bool:
        return self._running

    @property
    def paused(self) -> bool:
        return self._paused

    # ---------- 内部实现 ----------

    @staticmethod
    def _build_phases(work_sec: int, short_sec: int, long_sec: int,
                      short_count: int, loops: int) -> tuple:
        """根据配置构建阶段队列（时长单位均为秒），返回 (阶段队列, 每轮阶段数)。

        工作时间为 0 时跳过工作阶段（不产生 0 秒的阶段），
        队列全部由休息组成，实现"开始即休息、休息完还是休息"。
        """
        phases = []
        seg_per_loop = 0
        work = (PHASE_WORK, work_sec) if work_sec > 0 else None
        for _ in range(loops):
            for _ in range(short_count):
                if work is not None:
                    phases.append(work)
                    seg_per_loop += 1
                phases.append((PHASE_SHORT_REST, short_sec))
                seg_per_loop += 1
            if work is not None:
                phases.append(work)
                seg_per_loop += 1
            phases.append((PHASE_LONG_REST, long_sec))
            seg_per_loop += 1
        return phases, seg_per_loop

    def _emit_phase_changed(self) -> None:
        """广播当前阶段信息（含段与轮进度）。"""
        name, seconds = self._phases[self._index]
        seg_total = len(self._phases)
        loop_total = seg_total // self._seg_per_loop
        loop_cur = self._index // self._seg_per_loop + 1
        self.phase_changed.emit(name, seconds, self._index + 1, seg_total, loop_cur, loop_total)

    def _on_timeout(self) -> None:
        """每秒回调：递减剩余时间，归零后推进到下一阶段。"""
        if not self._running:
            return

        self._remaining -= 1
        if self._remaining > 0:
            self.tick.emit(self._remaining)
            return

        # 当前阶段倒计时归零
        name, _ = self._phases[self._index]
        self.phase_finished.emit(name)

        self._index += 1
        if self._index >= len(self._phases):
            self._running = False
            self._timer.stop()
            self.all_finished.emit()
            return

        self._remaining = self._phases[self._index][1]
        self._emit_phase_changed()
