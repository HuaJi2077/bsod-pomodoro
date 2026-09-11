"""程序入口：主窗口只负责页面导航与生命周期调度，业务逻辑委托给 logic 包

冷启动采用两阶段加载：阶段一仅导入 Qt 相关依赖，立即显示启动画面；
阶段二再加载重依赖（qt_material 主题、logic 业务逻辑链），装配完
主窗口后关闭启动画面。pygame / keyboard 等更重的库则延迟到
屏保 / 硬核模式首次使用时才导入（见 module/ 各实现）。
"""

import os

from PySide6.QtCore import QCoreApplication, Qt, QTimer, QTranslator
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QSplashScreen

from pages.main_window import Ui_MainWindow

from logic.settings import load_settings, save_settings

from utils import resource_path


class MainWindow(QMainWindow):
    """主窗口：只负责页面导航与生命周期调度，各页面业务逻辑委托给 logic 包。"""

    def __init__(self):
        super().__init__()
        # 重依赖延迟加载：logic 业务逻辑链较重，待启动画面出现后再导入
        from logic import PomodoroLogic, TrayController
        from logic.help import open_update_page, show_about, show_pomodoro_help

        # 创建 Ui_Form 的实例
        self.ui = Ui_MainWindow()
        # 将 UI 样式安装到自己身上
        self.ui.setupUi(self)
        # 锁定窗口宽高
        # self.setFixedSize(545, 645)
        # 帮助 / 关于菜单：简介弹窗与默认浏览器跳转
        self.ui.pomodoro.triggered.connect(lambda: show_pomodoro_help(self))
        self.ui.info.triggered.connect(lambda: show_about(self))
        self.ui.update.triggered.connect(open_update_page)
        # 切换颜色主题
        self.ui.light_white.triggered.connect(light_theme)
        self.ui.dark_black.triggered.connect(dark_theme)
        # 切换界面语言：中文回退源文本，英文加载 translate/ 下的 qm
        self.ui.chinese.triggered.connect(chinese_language)
        self.ui.english.triggered.connect(english_language)
        # 番茄钟主逻辑：交互控制与状态栏展示全部委托给 logic 层
        self.pomodoro_logic = PomodoroLogic(self.ui)
        # 托盘控制器：菜单"托盘化"转托盘，真正退出前先停表并解锁键鼠
        self.tray = TrayController(self, on_quit=self.pomodoro_logic.shutdown)
        # 普通弹窗模式的休息提醒可借托盘发送系统通知
        self.pomodoro_logic.set_notifier(self.tray.notify)
        # 窗口菜单：最小化（普通最小化，非托盘）；退出（直接退出，非托盘化）
        self.ui.minimize.triggered.connect(self.showMinimized)
        self.ui.exit.triggered.connect(self.tray.quit_app)

    def closeEvent(self, event):
        """点击关闭不退出程序：最小化至托盘后台运行；托盘不可用才真正退出。"""
        if self.tray.hide_to_tray():
            event.ignore()  # 拦截关闭，转入托盘
            return
        self.pomodoro_logic.shutdown()  # 托盘不可用，按原逻辑退出兜底
        super().closeEvent(event)

def light_theme():
    # qt_material（连带 jinja2）导入较重，首次应用主题时才加载（加快冷启动）
    from qt_material import apply_stylesheet

    # 设置亮色主题，这里设置两次主题才能正确显示汉字间距，切勿删除
    apply_stylesheet(app, theme='dark_red.xml')
    apply_stylesheet(app, theme='light_red.xml', invert_secondary=True)
    _settings["theme"] = "light"
    save_settings(_settings)

def dark_theme():
    # qt_material（连带 jinja2）导入较重，首次应用主题时才加载（加快冷启动）
    from qt_material import apply_stylesheet

    # 设置暗色主题，这里设置两次主题才能正确显示汉字间距，切勿删除
    apply_stylesheet(app, theme='light_red.xml', invert_secondary=True)
    apply_stylesheet(app, theme='dark_red.xml')
    _settings["theme"] = "dark"
    save_settings(_settings)

# 用户设置（主题 / 语言）：启动时加载，切换时写回 data/settings.json
_settings = load_settings()

# 当前已安装的翻译器（切换语言时先全部卸载再按需加载）
_translators = []

def _switch_language(lang: str):
    """切换界面语言：卸载旧翻译器并按需加载 qm，随后刷新已创建控件的文本。

    qm 由 pyside6-lrelease 编译 translate/ 下的 ts 得到；未翻译或 qm 缺失时
    回退源文本（中文）。UI 文本在 setupUi 时已固定，翻译器切换后必须调用
    retranslateUi 重新刷新。
    """
    for translator in _translators[:]:
        app.removeTranslator(translator)
        _translators.remove(translator)

    loaded = 0
    if lang == "en_US":
        # app.ts 覆盖 UI 层（MainWindow），code.ts 覆盖代码层（logic/services）
        for name in ("app", "code"):
            translator = QTranslator(app)
            if translator.load(str(resource_path(f"translate/{name}.qm"))):
                app.installTranslator(translator)
                _translators.append(translator)
                loaded += 1

    # 持久化语言设置
    _settings["language"] = lang
    save_settings(_settings)

    # 主窗口已创建时，刷新全部静态 UI 文本（菜单、按钮、标签等）
    if "window" in globals() and window is not None:
        window.ui.retranslateUi(window)
        window.pomodoro_logic.refresh_statusbar()
        if lang == "en_US" and loaded == 0:
            window.ui.statusbar.showMessage(
                QCoreApplication.translate("MainWindow", "未找到英文翻译文件（translate/*.qm 缺失），已回退中文"))

def chinese_language():
    # 简体中文：卸载全部翻译器，回退源文本（中文）
    _switch_language("zh_CN")

def english_language():
    # English：加载 translate/ 下编译好的 qm
    _switch_language("en_US")


# 屏蔽 Qt 加载 PNG 资源时可能出现的 libpng iCCP 警告
os.environ["QT_LOGGING_RULES"] = "qt.png.warning=false"

# 创建 QApplication
app = QApplication([])

# 主窗口：阶段二由 _startup 创建（创建前为 None，供语言切换函数判空）
window = None

# 启动画面：阶段一创建，两阶段加载期间给用户即时的视觉反馈
splash = None


def _startup():
    """启动阶段二：加载重依赖并装配主窗口（此时启动画面已在屏）。"""
    global window
    # 语言必须在创建窗口前应用：setupUi 末尾的 retranslateUi 才能直接产出对应语言
    _switch_language(_settings["language"])
    window = MainWindow()
    # 按持久化设置恢复主题（默认亮色）；qt_material 在此处才首次导入
    dark_theme() if _settings["theme"] == "dark" else light_theme()
    window.show()
    splash.finish(window)


if __name__ == "__main__":
    """应用入口：先以纯 Qt 依赖显示启动画面，再延迟加载其余模块进入主循环"""
    # 阶段一：仅 Qt 依赖即可拉起启动画面，用户第一时间看到程序已启动
    splash = QSplashScreen(QPixmap(str(resource_path("icon/logo.png"))))
    splash.show()
    splash.showMessage(QCoreApplication.translate("MainWindow", "正在启动，请稍候…"),
                       alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
    app.processEvents()  # 立即绘制启动画面，不等事件循环
    # 阶段二：推迟到事件循环启动后执行，保证启动画面先行渲染、首帧不被阻塞
    QTimer.singleShot(0, _startup)
    app.exec()
