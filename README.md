# PyMeshCore GUI

**PyMeshCore GUI** is an open-source desktop application for interacting with the MeshCore network.
It focuses on **chatting, prototyping, and development** on top of MeshCore, with an emphasis on
desktop workflows and developer accessibility.

The project is built using **PySide6 (Qt for Python)** and **meshcore-py**.

This is an early, experimental release.

---

## Motivation

MeshCore provides powerful mesh networking capabilities, but existing clients are closed source.
PyMeshCore GUI aims to explore what an **open, extensible desktop client** can look like, while also
serving as a platform for experimentation and future development.

The long-term vision is a **full Qt-based stack**, potentially including a native C++ core
(`QMeshCore`) with a clean GUI layered on top.

---

## Features (Current)

- Desktop GUI built with PySide6
- MeshCore connectivity via `meshcore-py`
- Chat-oriented interface
- Designed for experimentation and prototyping
- Cross-platform (where supported by dependencies)

---

## Installation

This project uses **uv**.

```bash
uv sync
```

---

## Running

```bash
uv run meshcore-gui
```

---

## Project Status

PyMeshCore GUI is under active development and should be considered alpha software.
APIs, UI, and internal structure may change at any time.

Contributions, feedback, and experimentation are welcome.

---

## License

This project is licensed under the GNU General Public License v3 (GPLv3).
