# D-CATT

### Developer's Configurable Advanced Terminal Toolkit

D-CATT is a modern, customizable, cross-platform terminal emulator built with **Python and PySide6**.

It is designed for developers who want a terminal that is simple to use out of the box while still providing deep customization through human-readable configuration files.

---

## ✨ Features

* 🖥️ **Cross-platform** — Linux, Windows and macOS
* 🎨 **Customizable appearance** — fonts, colors, cursor, opacity and more
* ⚙️ **JSON-based configuration**
* ⌨️ **Custom keyboard shortcuts**
* 🎭 **Built-in themes and configuration presets**
* 📑 **Multiple terminal tabs**
* 🐚 **Native shell support**
* ⚡ **Responsive asynchronous terminal I/O**
* 🔧 **Graphical settings interface**
* 📝 **Direct configuration through editable files**
* 📦 **Standalone application releases**

---

## ⚙️ Configuration

D-CATT follows a **configuration-first approach**.

Users can configure the terminal through the graphical settings interface or directly edit its human-readable configuration files.

Example:

```json
{
    "font_family": "JetBrains Mono",
    "font_size": 14,
    "cursor_style": "block",
    "scrollback": 10000
}
```

Configuration can be separated into different files for different aspects of the terminal, such as:

```text
D-CATT/
└── config/
    ├── config.json
    ├── keybindings.json
    └── themes/
        ├── default.json
        ├── nord.json
        └── dracula.json
```

This makes D-CATT highly customizable without requiring users to modify the source code.

---

## 🏗️ Architecture

D-CATT separates the graphical interface, terminal core and operating-system-specific functionality.

```text
D-CATT
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
├── Systems
│   ├── Linux
│   ├── Windows
│   └── macOS
│
└── Utilities
```

This architecture keeps platform-specific functionality separated while allowing the main terminal logic to remain portable.

---

## 🛠️ Built With

* **Python**
* **PySide6**
* **PTY / ConPTY**
* **SQLite**
* **JSON**

---

## 🎯 Philosophy

> **Simple by default. Powerful when customized.**

D-CATT is built around the idea that customization should not require sacrificing convenience.

Users who simply want a terminal can launch D-CATT and start working immediately.

Power users can open the configuration files and customize the experience to their exact preferences.

---

## 📦 Installation

D-CATT is distributed as a standalone application for supported platforms.

Download the appropriate release for your operating system from **GitHub Releases**, install or extract it, and start using D-CATT without manually installing Python or project dependencies.

### 🛠️ Running from Source

For development:

```bash
git clone https://github.com/realmanish96-source/Terminal.git
cd Terminal
pip install -r requirements.txt
python main.py
```

---

## 📁 Project Structure

```text
Terminal/
│
├── main.py
├── README.md
├── requirements.txt
├── LICENSE
│
└── app/
    ├── core/
    ├── gui/
    ├── systems/
    └── utils/
```

---

## 🤝 Contributing

Contributions, suggestions and improvements are welcome.

If you find a bug or have an idea that could improve D-CATT, feel free to open an issue or submit a pull request.

---

## 📄 License

D-CATT is released under the **MIT License**.

Copyright © 2026 Expensive Money.
