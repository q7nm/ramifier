# Ramifier

![Python](https://img.shields.io/badge/python-3.9+-blue?style=flat)
![License](https://img.shields.io/badge/license-GPL--3.0-red?style=flat)
![Version](https://img.shields.io/github/v/release/q7nm/ramifier?label=version&style=flat)
![Stars](https://img.shields.io/github/stars/q7nm/ramifier?style=flat)

**Ramifier** is a Python tool that moves selected directories into RAM (tmpfs) to speed up access and reduce disk wear. It automatically creates backups, monitors changes, and restores directories when needed.

---

## Features

- Move directories to RAM (`/dev/shm` or `/tmp`) for faster operations.
- Automatic backup with Zstandard compression.
- Tracks file changes for automatic backups.
- Restore from backup or RAM seamlessly.
- Configurable dynamic backup intervals.
- Safe daemon operation with lock file support.
- Supports multiple targets with individual settings.

## Dependencies

Ramifier requires the following Python packages:

- pyyaml
- psutil
- pyxdg
- zstandard

## Wiki

For detailed documentation, guides, and advanced usage, visit the [Ramifier Wiki](https://github.com/q7nm/ramifier/wiki).

---

## License

This project is licensed under **GPL-3.0**. See the [LICENSE](LICENSE) file for details.
