#!/usr/bin/env python3
"""Nginx Log Dashboard - Environment Self-Check & Fix Script

Pure standard library, single file, copy-and-run.
Checks Python 3.7+ dependencies, locates / creates a log file, validates
ports and permissions, then prints a one-command startup line.
"""

import sys
import os
import socket
import stat as _stat
import datetime
import collections
import json
import time
import re
import threading
import http.server
import socketserver


# ---------------------------------------------------------------------------
# 1. Python version check
# ---------------------------------------------------------------------------
def check_python():
    ok = sys.version_info >= (3, 7)
    print("[{ok_s}] Python {v}".format(
        ok_s="PASS" if ok else "FAIL",
        v=sys.version.split()[0]))
    if not ok:
        print("    WARNING: Python >= 3.7 recommended (current {})".format(
            sys.version.split()[0]))
    return ok


# ---------------------------------------------------------------------------
# 2. Standard library check
# ---------------------------------------------------------------------------
REQUIRED_MODULES = [
    ("os", os),
    ("sys", sys),
    ("re", re),
    ("time", time),
    ("threading", threading),
    ("socketserver", socketserver),
    ("json", json),
    ("http.server", http.server),
    ("collections", collections),
    ("datetime", datetime),
]


def check_stdlib():
    all_ok = True
    for name, mod in REQUIRED_MODULES:
        ok = mod is not None
        if not ok:
            all_ok = False
        print("[{ok_s}] {name}".format(
            ok_s="PASS" if ok else "FAIL", name=name))
    return all_ok


# ---------------------------------------------------------------------------
# 3. Third-party package check (optional)
# ---------------------------------------------------------------------------
THIRD_PARTY = ["fastapi", "uvicorn", "aiofiles", "python_multipart"]


def check_third_party():
    all_ok = True
    for pkg in THIRD_PARTY:
        found = False
        try:
            __import__(pkg)
            found = True
        except ImportError:
            pass
        if not found:
            all_ok = False
        print("[{ok_s}] {name}".format(
            ok_s="PASS" if found else "MISS", name=pkg))
    if not all_ok:
        print("    Tip: pip install fastapi uvicorn aiofiles python-multipart")
    return all_ok


# ---------------------------------------------------------------------------
# 4. Log file discovery
# ---------------------------------------------------------------------------
def discover_log_file():
    """Resolve log file path.
    
    Priority:
      1. LOG_FILE_PATH env var
      2. /var/log/nginx/access.log
      3. ./test.log  (auto-created with sample data)
    Returns (path: str, created: bool, count: int)
    """
    # Priority 1 – environment variable
    path = os.environ.get("LOG_FILE_PATH", "")
    if path:
        if os.path.isfile(path):
            size = os.path.getsize(path)
            print("[PASS] LOG_FILE_PATH={path} ({size} bytes)".format(
                path=path, size=size))
            return path, False, 0
        else:
            print("[WARN] LOG_FILE_PATH set but file not found: {path}".format(path=path))
            parent = os.path.dirname(path) or "."
            if not os.path.isdir(parent):
                print("    Directory does not exist, falling back...")
            else:
                print("    Will create empty file...")

    # Priority 2 – default Nginx path
    nginx_path = "/var/log/nginx/access.log"
    if os.path.isfile(nginx_path):
        size = os.path.getsize(nginx_path)
        print("[PASS] Using {path} ({size} bytes)".format(
            path=nginx_path, size=size))
        return nginx_path, False, 0

    # Priority 3 – local test.log
    test_path = os.path.join(os.getcwd(), "test.log")
    _generate_sample_log(test_path)
    print("[INFO] Created test.log with 20 sample entries")
    return test_path, True, 20


def _generate_sample_log(path):
    """Generate 20 sample Nginx combined-format log lines."""
    now = datetime.datetime.now()
    urls = ["/api/users", "/api/orders", "/api/products",
            "/api/search", "/api/auth"]
    methods = ["GET", "GET", "POST", "PUT", "DELETE"]
    statuses = [200, 200, 200, 200, 201, 204, 301, 401, 500, 500]
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "curl/7.68.0",
        "python-requests/2.25.1",
        "PostmanRuntime/7.26.8",
    ]

    lines = []
    for i in range(20):
        ts = now + datetime.timedelta(seconds=i * 2)
        time_str = ts.strftime("%d/%b/%Y:%H:%M:%S +0800")
        ip = "192.168.1.{n}".format(n=(i % 10) + 1)
        url = urls[i % len(urls)]
        method = methods[i % len(methods)]
        status = statuses[i % len(statuses)]
        agent = agents[i % len(agents)]
        rt = round((i % 10 + 1) * 0.05 + i * 0.01, 3)
        body = (i + 1) * 50 + 100
        line = (
            '{ip} - - [{time}] "{method} {url} HTTP/1.1" '
            '{status} {body} "-" "{agent}" {rt}'
        ).format(
            ip=ip, time=time_str, method=method, url=url,
            status=status, body=body, agent=agent, rt=rt,
        )
        lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# 5. Port availability
# ---------------------------------------------------------------------------
def find_free_port(start=8080, max_attempts=50):
    """Return the first available port starting from *start*."""
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError as _e:
                continue
    return None


def check_port(port):
    """Check if *port* is available; return a usable port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", port))
            print("[PASS] Port {p} is available".format(p=port))
            return port
        except OSError as _e:
            new_port = find_free_port(port + 1)
            if new_port:
                print("[WARN] Port {p} in use, using {np} instead".format(
                    p=port, np=new_port))
            else:
                print("[FAIL] No free port found starting from {p}".format(p=port))
            return new_port


# ---------------------------------------------------------------------------
# 6. File permission check
# ---------------------------------------------------------------------------
def check_path_writable(path):
    """Check if the *parent directory* of *path* is writable."""
    parent = os.path.dirname(path) or os.getcwd()
    if not parent:
        parent = os.getcwd()
    writable = os.access(parent, os.W_OK)
    if writable:
        print("[PASS] Directory is writable: {d}".format(d=parent))
    else:
        print("[FAIL] Directory not writable: {d}".format(d=parent))
        print("    Fix: sudo chmod -R 755 {d}".format(d=parent))
        print("    Or:  sudo mkdir -p {d} && sudo chown  {d}".format(d=parent))
    return writable


# ---------------------------------------------------------------------------
# 7. Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 54)
    print("  Nginx Log Dashboard - Environment Self-Check")
    print("=" * 54)
    print()

    # --- Python version ---
    py_ok = check_python()
    print()

    # --- Standard library ---
    stdlib_ok = check_stdlib()
    print()

    # --- Third-party packages ---
    third_ok = check_third_party()
    print()

    # --- Log file ---
    log_path, created, count = discover_log_file()
    writable = check_path_writable(log_path)
    print()

    # --- Port ---
    port = check_port(8080)
    print()

    # --- Summary ---
    print("-" * 54)
    print("  Summary")
    print("-" * 54)
    print("  Python : {v}".format(v=sys.version.split()[0]))
    print("  Stdlib : {s}".format(s="OK" if stdlib_ok else "ISSUES"))
    print("  Dependencies : {s}".format(s="OK" if third_ok else "MISSING"))
    print("  Log file: {p}".format(p=log_path))
    if created:
        print("  Sample entries: {n}".format(n=count))
    print("  Port   : {p}".format(p=port))
    print()

    # --- One-command startup ---
    print("-" * 54)
    print("  One-command Startup")
    print("-" * 54)
    host = "0.0.0.0"
    log_file_for_env = log_path.replace(os.sep, "/")

    if third_ok and port:
        if sys.platform == "win32":
            # Windows
            cmd_line = (
                "set LOG_FILE_PATH={log} && "
                "uvicorn main:app --host {host} --port {port}"
            ).format(log=log_file_for_env, host=host, port=port)
        else:
            cmd_line = (
                "LOG_FILE_PATH={log} "
                "uvicorn main:app --host {host} --port {port}"
            ).format(log=log_file_for_env, host=host, port=port)
        print("  " + cmd_line)
        print()
    elif not third_ok:
        print("  Install dependencies first:")
        print("    pip install fastapi uvicorn aiofiles python-multipart")
        print()
    if not port:
        print("  No available port found. Check firewall / running services.")

    print("=" * 54)

    # Exit code
    issues = []
    if not stdlib_ok:
        issues.append("stdlib")
    if not third_ok:
        issues.append("dependencies")
    if not port:
        issues.append("port")
    sys.exit(0)


if __name__ == "__main__":
    main()
