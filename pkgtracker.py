#!/usr/bin/env python3
import os
import sqlite3
import re
import subprocess
import argparse
import sys
from pathlib import Path
import sys

HELP_TEXT = """
pkgtracker - Unified Package Tracker for Linux
------------------------------------------------
Tracks installed packages from APT, DPKG, SNAP, and HOMEBREW into an SQLite DB.

Usage:
  pkgtracker [options]

Options:
  --list [manager]     List tracked packages. Manager can be: apt, dpkg, snap, brew, all.
  --refresh            Refresh the database by scanning all managers.
  --help               Show this help message and exit.

Examples:
  pkgtracker --list apt
  pkgtracker --refresh
  pkgtracker --list all

Database:
  Stored at ~/.local/share/pkgtracker/pkgtracker.db

Integration:
  Automatically updates after APT operations via /etc/apt/apt.conf.d/99pkgtracker.
  Optional cron job or systemd timer keeps it synced with Snap/Brew.

Author:
  JD — github.com/JD-01-DEV
"""

if "--help" in sys.argv:
    print(HELP_TEXT)
    sys.exit(0)


DB_PATH = os.getenv("PKGTRACKER_DB", "/var/lib/pkgtracker/pkgtracker.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS packages (
                name TEXT NOT NULL,
                manager TEXT NOT NULL,
                PRIMARY KEY(name, manager)
            )''')
conn.commit()

def add_package(name, manager):
    c.execute('INSERT OR IGNORE INTO packages (name, manager) VALUES (?, ?)', (name, manager))
    conn.commit()

def remove_package(name, manager):
    c.execute('DELETE FROM packages WHERE name = ? AND manager = ?', (name, manager))
    conn.commit()

# --- APT Tracking ---
def parse_apt():
    try:
        logfiles = sorted(Path('/var/log/apt').glob('history.log*'))
        for logfile in logfiles:
            try:
                with open(logfile, 'r', errors='ignore') as f:
                    content = f.read()
            except Exception:
                continue

            # Detect explicit install/remove commands from apt history
            for match in re.finditer(r'Commandline:\s+(sudo\s+)?apt(?:-get)?\s+(install|remove)\s+([^\n]+)', content):
                action = match.group(2)
                packages_str = match.group(3)
                pkgs = [re.split(r'[= ]', p.strip())[0] for p in packages_str.split() if not p.startswith('-')]
                for pkg in pkgs:
                    if action == 'install':
                        add_package(pkg, 'apt')
                    elif action == 'remove':
                        remove_package(pkg, 'apt')
    except Exception:
        pass

# --- DPKG Tracking ---
def parse_dpkg():
    try:
        result = subprocess.run(['grep', '-E', 'install |remove ', '/var/log/dpkg.log'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 4:
                action = parts[2]
                pkg = parts[3].split(':')[0]
                if action == 'install':
                    add_package(pkg, 'dpkg')
                elif action == 'remove':
                    remove_package(pkg, 'dpkg')
    except Exception:
        pass

# --- SNAP Tracking ---
def parse_snap():
    try:
        snaps = subprocess.run(['snap', 'list'], capture_output=True, text=True).stdout.splitlines()[1:]
        installed = [line.split()[0] for line in snaps if line.strip()]
        c.execute('SELECT name FROM packages WHERE manager = ?', ('snap',))
        existing = {row[0] for row in c.fetchall()}

        for pkg in set(installed) - existing:
            add_package(pkg, 'snap')
        for pkg in existing - set(installed):
            remove_package(pkg, 'snap')
    except Exception:
        pass

# --- HOMEBREW Tracking ---
def parse_homebrew():
    try:
        installed = subprocess.run(['brew', 'list'], capture_output=True, text=True).stdout.splitlines()
        c.execute('SELECT name FROM packages WHERE manager = ?', ('brew',))
        existing = {row[0] for row in c.fetchall()}

        for pkg in set(installed) - existing:
            add_package(pkg, 'brew')
        for pkg in existing - set(installed):
            remove_package(pkg, 'brew')
    except Exception:
        pass

# --- Listing ---
def list_packages(manager=None):
    if manager is None or manager == 'all':
        data = list(c.execute('SELECT manager, name FROM packages ORDER BY manager, name'))
        if not data:
            print("No packages recorded yet.")
        else:
            for mgr, name in data:
                print(f"{mgr}\t{name}")
    else:
        data = list(c.execute('SELECT name FROM packages WHERE manager = ? ORDER BY name', (manager,)))
        if not data:
            print(f"No packages found for manager: {manager}")
        else:
            for (name,) in data:
                print(name)

def main():
    parser = argparse.ArgumentParser(description="Track installed packages across multiple managers.")
    parser.add_argument('--list', nargs='?', const='all', help='List packages (optional: apt, dpkg, snap, brew, all)')
    parser.add_argument('--refresh', action='store_true', help='Force refresh all package lists')
    args = parser.parse_args()

    if args.list:
        list_packages(args.list)
        conn.close()
        sys.exit(0)

    if args.refresh:
        parse_apt()
        parse_dpkg()
        parse_snap()
        parse_homebrew()
        print("Package data refreshed.")
        conn.close()
        sys.exit(0)

    # Default behavior: just sync logs
    parse_apt()
    parse_dpkg()
    parse_snap()
    parse_homebrew()

if __name__ == '__main__':
    main()
    conn.close()
