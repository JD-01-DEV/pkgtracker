# 🧠 pkgtracker — Universal Package Installation Tracker

`pkgtracker` is a lightweight, cross-distribution terminal tool that automatically tracks every package you **install** or **remove** across major Linux package managers — including **APT**, **dpkg**, **Snap**, and **Homebrew** — while recording only **explicit user installs** in a local SQLite database.

---

## ✨ Features

- Detects installations and removals from:
  - **APT / apt-get**
  - **dpkg**
  - **Snap**
  - **Homebrew**
- Maintains a single database at `/var/lib/pkgtracker/pkgtracker.db`
- Auto-refreshes hourly using a **systemd timer**
- Adds a post-install **APT hook** for real-time updates
- No daemon — runs quickly and exits
- Works on all major Linux distributions (Ubuntu, Pop!_OS, Fedora, Arch, openSUSE, etc.)
- Includes a **clean uninstaller**

---

## 🚀 Installation

Run this one-liner (works on any Linux distro):

```bash
curl -sSL https://raw.githubusercontent.com/JD-01-DEV/pkgtracker/main/install_pkgtracker.sh | bash
````

The installer:

* Detects your package manager (`apt`, `dnf`, `pacman`, `zypper`, etc.)
* Installs required tools (`python3`, `sqlite3`, `systemd`)
* Copies the main script to `/usr/local/bin/pkgtracker`
* Sets up a systemd timer to run every hour
* Adds an APT post-install hook (if APT is available)

---

## 🧹 Uninstallation

To remove `pkgtracker` completely:

```bash
curl -sSL https://raw.githubusercontent.com/JD-01-DEV/pkgtracker/main/uninstall_pkgtracker.sh | bash
```

Removes:

* `/usr/local/bin/pkgtracker`
* `/etc/systemd/system/pkgtracker.service`
* `/etc/systemd/system/pkgtracker.timer`
* `/var/lib/pkgtracker`
* `/etc/apt/apt.conf.d/99pkgtracker` (if exists)

---

## 🧰 Usage

### List all tracked packages

```bash
pkgtracker --list
```

### List by package manager

```bash
pkgtracker --list apt
pkgtracker --list snap
pkgtracker --list brew
pkgtracker --list dpkg
```

### Manually refresh

```bash
sudo pkgtracker
```

### View help

```bash
pkgtracker --help
```

---

## 🗂 Database Structure

SQLite DB path: `/var/lib/pkgtracker/pkgtracker.db`

| name | manager |
| ---- | ------- |
| nmap | apt     |
| curl | brew    |
| vlc  | snap    |

---

## 🔧 Manual Installation (Developers)

Clone the repository:

```bash
git clone https://github.com/JD-01-DEV/pkgtracker.git
cd pkgtracker
```

Install manually:

```bash
sudo ./install_pkgtracker.sh
```

Run directly:

```bash
python3 pkgtracker.py
```

Uninstall:

```bash
sudo ./uninstall_pkgtracker.sh
```

---

## 🧩 Requirements

* **Python ≥ 3.6**
* **SQLite3**
* **systemd** (for scheduled runs)
* **sudo** privileges

All dependencies are installed automatically by the installer if not already present.

---

## 🧪 Roadmap (Future feature)

* [ ] Add support for `flatpak` and `pacman`
* [ ] Add `--export` / `--import` commands for backup & restore
* [ ] JSON / CSV export format
* [ ] Optional desktop notifications for new or removed packages
* [ ] Integration with GUI front-end

---

## ⚙️ Project Files

| File                                | Description                  |
| ----------------------------------- | ---------------------------- |
| `pkgtracker.py`                     | Main package tracking script |
| `install_pkgtracker.sh`             | Distro-agnostic installer    |
| `uninstall_pkgtracker.sh`           | Complete uninstaller         |
| `requirements.txt`                  | Python environment info      |
| `/var/lib/pkgtracker/pkgtracker.db` | SQLite package log           |
| `/etc/systemd/system/pkgtracker.*`  | Timer & service              |

---

## 💡 Example Output

```bash
$ pkgtracker --list all
apt     nmap
apt     htop
brew    curl
snap    vlc
```

---

## 🧱 requirements.txt

See [requirements.txt](./requirements.txt) for Python dependencies.

---

## ⚖️ License

MIT License © 2025 [JD](https://github.com/JD-01-DEV)

---

## 🧠 Contributing

Pull requests and improvements are welcome!
If you want to add new package manager support or optimize the log parsing, open an issue or PR.

---

## 🌐 Links

* **Repository:** [https://github.com/JD-01-DEV/pkgtracker](https://github.com/JD-01-DEV/pkgtracker)
* **Author:** JD
* **License:** MIT

