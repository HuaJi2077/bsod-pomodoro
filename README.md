<img src="./icon/logo.png" alt="Logo" width="128" />

<h1 align="center">BSOD Pomodoro 蓝屏番茄钟</h1>

[English](./README_EN.md) | 简体中文

**一款会「伪装蓝屏」的番茄钟：休息时既能伪装成蓝屏死机、彩虹猫病毒，也支持正常提醒，让你休息得名正言顺，不再被老板诟病。也能用来整蛊好友，让他误以为电脑真的蓝屏，大吃一惊。**

**A pomodoro timer that can "fake a crash": during breaks it can disguise itself as a Blue Screen of Death, the Nyan Cat virus, or simply show a normal reminder — so your rest is well justified and beyond the boss's reproach. It can also be used to prank a friend, making them believe the computer has really crashed.**

<br>

**软件界面：**

<img src="./icon/interface.png" alt="Interface" width="40%" />

**蓝屏界面：**

<img src="./icon/blue_screen.png" alt="BlueScreen" width="60%" />

**彩虹猫：**

<img src="./icon/nyan_cat.png" alt="NyanCat" width="60%" />

## 📖 目录

- [✨ 功能特点](#-功能特点)
- [📥 获取运行](#-获取运行)
- [🛠️ 使用说明](#️-使用说明)
- [🏗️ 项目架构](#️-项目架构)
- [🌍 开源引用](#-开源引用)
- [⚖️ 免责声明](#️-免责声明)

## ✨ 功能特点

- ⏱️ **标准番茄钟**：工作 / 短休息 / 长休息完整循环，可配置短休次数与番茄个数，运行状态实时显示在状态栏。
- 🎭 **伪装休息**：休息时可将全屏屏保险装成「蓝屏死机」或「彩虹猫」病毒 GIF 动画，也支持普通弹窗 + 系统通知提醒。
- 😈 **整蛊好友**：内置整蛊模式，可以长时间显示「蓝屏死机」或「彩虹猫」病毒画面，让好朋友大吃一惊**。注意：整蛊好友时切勿开启硬核模式；如遇任何问题由使用者自行承担。**
- 🔒 **硬核模式**：可以在休息期间锁定键盘和鼠标，强制进行休息；一定要谨慎使用，切勿对他人电脑使用。
- 🗂️ **预设 / 自定义**：内置标准、整蛊两种预设；自定义模式下可以保存你自己的番茄钟配置。
- 🌗 **明暗主题**：支持亮色 / 暗色双主题一键切换。
- 🌐 **中英双语**：界面完整国际化，通过菜单切换语言。
- 📌 **托盘驻留**：关闭窗口最小化到系统托盘后台继续运行，托盘菜单可恢复或退出。
- 📦 **开箱即用**：一条命令打包为单文件、无控制台窗口的独立 exe。

> [!WARNING]
> **硬核模式**会禁用键盘和鼠标，休息期间无法正常退出，可以使用 **Ctrl+Alt+Del** 唤出系统界面尝试自救。

## 📥 获取运行

### 方式一：从 Releases 下载

前往 [Releases 页面](https://github.com/HuaJi2077/bsod-pomodoro/releases) 下载最新的软件，双击即可运行。

### 方式二：从源码运行

```bash
git clone https://github.com/HuaJi2077/bsod-pomodoro
cd bsod-pomodoro
uv sync
uv run python main.py
```

### 方式三：自行打包软件

```bash
git clone https://github.com/HuaJi2077/bsod-pomodoro
cd bsod-pomodoro
uv sync                              # 同步依赖
uv run python script/build_qm.py     # 编译翻译文件（.qm）
uv run python script/build_exe.py    # 打包单文件（exe）
```

打包产物会输出至 `output/BSOD_Pomodoro.exe`

## 🛠️ 使用说明

1. **选择预设**：标准番茄钟 / 整蛊模式 / 自定义；选择「自定义」后可自由调整工作时间、短休 / 长休时间、短休次数与番茄个数，改动会自动保存。
2. **选择休息屏保**：蓝屏死机 / 彩虹猫 / 普通提示。
3. **硬核模式**（休息期间锁定键鼠，强制进行休息，**慎用**）。
4. **开始计时**，运行期间可暂停 / 继续 / 停止，进度实时显示在状态栏。
5. **休息期间**按所选屏保全屏展示（普通提示则弹出模态提醒并发送系统通知），休息结束自动恢复。

> [!TIP]
> 关闭窗口不会退出程序——它会驻留系统托盘继续计时，从托盘菜单可以恢复窗口或真正退出。

## 🏗️ 项目架构

基于 Presentation / Logic / Service 三层分层的 PySide6 桌面应用，依赖与虚拟环境统一由 [uv](https://docs.astral.sh/uv/) 管理：

- **依赖管理**：依赖声明在 `pyproject.toml`，`uv.lock` 锁定精确版本，保证不同环境构建一致；
- **一键同步**：`uv sync` 自动创建 `.venv` 并安装全部依赖，无需手动 pip；
- **统一入口**：所有脚本（运行、翻译编译、打包）均通过 `uv run` 执行，始终使用项目虚拟环境，避免环境污染。

```text
用户操作
   │ 控件信号
   ▼
logic/                     逻辑层：交互控制、状态维护、更新 UI
   │ service.run(...)
   ▼
services/                  服务层：计时调度、屏保 / 键鼠锁定封装
   │ signal（自动回到主线程）
   ▼
pages/                     UI 层：控件声明与布局（无业务代码）
```

```text
Pomodoro_BSOD/
├── main.py                 # 入口：主窗口装配、主题与语言切换
├── pyproject.toml          # 依赖声明（uv 管理）
├── uv.lock                 # 依赖版本锁定
├── pages/                  # UI 层（Qt Designer 产物）
├── logic/                  # 逻辑层（番茄钟 / 托盘 / 帮助）
├── services/               # 服务层（计时 / 屏保 / 硬核锁定）
├── module/                 # 第三方屏保模块（见下方开源引用）
├── translate/              # Qt Linguist 翻译源文件（.ts）
├── data/presets.json       # 预设与自定义配置
├── icon/                   # 图标与截图
├── script/                 # 翻译编译 / 打包脚本
```

## 🌍 开源引用

本项目在 [module/](./module) 目录中引用并改造了以下开源仓库，感谢原作者的贡献：

引用时保留了各仓库的版权与许可声明，并在原始实现基础上做了包化改造和部分修改。

| 模块 | 来源仓库 | 许可证 | 用途 |
| :-- | :-- | :-- | :-- |
| [module/blue_screen](./module/blue_screen) | [arpy8/bsod](https://github.com/arpy8/bsod) | [MIT](./module/blue_screen/LICENSE) | 蓝屏死机屏保 |
| [module/nyan_cat](./module/nyan_cat) | [borealkiss/nyancat.py](https://github.com/borealkiss/nyancat.py) | [Apache-2.0](./module/nyan_cat/LICENSE) | 彩虹猫动画屏保 |

## ⚖️ 免责声明

- 本软件仅供个人学习与合法用途的休息提醒，**请勿用于恶意破坏、欺骗或骚扰他人**。
- 硬核模式会在休息期间锁定键盘和鼠标，请确保了解风险后再启用；虽然程序退出时会自动解锁，但仍建议谨慎使用。
- 因使用本软件产生的任何后果由使用者自行承担。

## 📜 许可证

本项目基于 [MIT 许可证](./LICENSE) 发布，欢迎自由使用和二次开发。
