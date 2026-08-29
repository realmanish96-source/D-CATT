# MyTerminal

A modern, customizable, cross-platform terminal emulator built with **Python and PySide6**.

MyTerminal is designed to provide a clean terminal experience out of the box while giving users complete control over how their terminal looks and behaves.

## ✨ Features

* 🖥️ Cross-platform support for **Linux, Windows and macOS**
* 🎨 Customizable fonts, colors, cursor and terminal appearance
* ⚙️ **JSON-based configuration** for advanced customization
* ⌨️ Fully customizable keyboard shortcuts
* 🎭 Built-in themes and configuration presets
* 📑 Multiple terminal tabs
* 🐚 Uses the system's native shell
* ⚡ Responsive, asynchronous terminal I/O
* 🔧 GUI settings for users who prefer a graphical interface
* 📝 Direct configuration through human-readable files
* 📦 Standalone releases that can be installed and used without manually setting up Python or dependencies

## ⚙️ Configuration

MyTerminal follows a configuration-first approach.

Instead of forcing users to configure everything through a graphical settings panel, important settings are stored in simple, human-readable JSON files.

Example:

```json
{
    "font_family": "JetBrains Mono",
    "font_size": 14,
    "cursor_style": "block",
    "scrollback": 10000
}
```

Users can modify their configuration directly or use the built-in settings interface.

Themes, keyboard shortcuts and other preferences can be customized independently, making the terminal easy to personalize without modifying the source code.

## 🏗️ Architecture

MyTerminal separates the user interface from the terminal backend and platform-specific functionality.

```text
MyTerminal
│
├── GUI
│   ├── Main Window
│   ├── Terminal Tabs
│   └── Settings
│
├── Core
│   ├── Terminal Sessions
│   ├── PTY / ConPTY
│   ├── ANSI Parser
│   └── Configuration
│
└── Platform Layer
    ├── Linux
    ├── Windows
    └── macOS
```

This allows the core terminal functionality to remain independent from the operating system while platform-specific implementations handle the differences between Linux, Windows and macOS.

## 🛠️ Built With

* **Python**
* **PySide6**
* **PTY / ConPTY**
* **SQLite**
* **JSON**

## 🎯 Philosophy

MyTerminal follows a simple principle:

> **Simple by default. Powerful when customized.**

The goal is not to overwhelm users with configuration, while still providing enough control for users who want to fine-tune their terminal through configuration files.

## 📥 Installation

MyTerminal is distributed as a standalone application for supported platforms.

Users can download the appropriate release from **GitHub Releases**, install or extract it, and start using the terminal without manually installing Python or project dependencies.

### Development

Developers can run the project directly from source:

```bash
git clone https://github.com/realmanish96-source/Terminal.git
cd Terminal
pip install -r requirements.txt
python main.py
```

## 📄 License

MyTerminal is released under the **MIT License**.
