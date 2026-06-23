#!/usr/bin/env python3
"""Nginx Log Dashboard - 离线环境一键部署脚本

适用于与互联网完全隔离的内网环境。
纯标准库，无需任何第三方依赖。

使用方法：
    1. 将整个项目目录（含 pylib/ 和 static/）复制到内网机器
    2. 运行本脚本：
       python3 deploy_offline.py

    脚本自动完成：
      - 诊断 Python 环境
      - 检查离线依赖包
      - 配置 PYTHONPATH 使用内置 pylib/
      - 检查/创建日志文件
      - 检查端口可用性
      - 输出启动命令
"""

import sys
import os
import platform
import socket
import shutil
import subprocess
import json
import time
import re
import threading
import datetime
import collections
import ast
import importlib
import http.server
import socketserver


# 项目根目录（本脚本所在目录）
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PYLIB_DIR = os.path.join(PROJECT_DIR, "pylib_py37")
STATIC_DIR = os.path.join(PROJECT_DIR, "static")
STATIC_VENDOR_DIR = os.path.join(STATIC_DIR, "vendor")


def _installed_version(package_name: str, module) -> str:
    version = getattr(module, "__version__", None)
    if version:
        return str(version)
    prefix = package_name.replace("-", "_").lower() + "-"
    for entry in os.listdir(PYLIB_DIR):
        if entry.lower().startswith(prefix) and entry.endswith(".dist-info"):
            metadata_path = os.path.join(PYLIB_DIR, entry, "METADATA")
            try:
                with open(metadata_path, "r", encoding="utf-8") as metadata:
                    for line in metadata:
                        if line.startswith("Version:"):
                            return line.split(":", 1)[1].strip()
            except OSError:
                pass
    return "unknown"


def print_header(title: str) -> None:
    print()
    print("-" * 54)
    print(f"  {title}")
    print("-" * 54)


def check_python_version() -> bool:
    ok = sys.version_info >= (3, 7)
    print(f"[{'PASS' if ok else 'FAIL'}] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    if not ok:
        print("    Python >= 3.7 is required")
    machine = platform.machine() or "unknown"
    system = platform.platform()
    print(f"[INFO] Platform: {system}")
    print(f"[INFO] Machine : {machine}")
    if machine.lower() not in ("aarch64", "arm64"):
        print("[WARN] 当前机器不是 ARM64；麒麟 V10 ARM 部署前请在目标机器运行本脚本复检")
    return ok


def check_stdlib() -> bool:
    modules = [
        ("os", os), ("sys", sys), ("re", re), ("time", time),
        ("threading", threading), ("socketserver", socketserver),
        ("json", json), ("http.server", http.server),
        ("collections", collections), ("datetime", datetime),
    ]
    all_ok = True
    for name, mod in modules:
        ok = mod is not None
        if not ok:
            all_ok = False
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    return all_ok


def check_offline_deps() -> bool:
    """Check if pylib/ contains all necessary packages by trying to import them."""
    print()
    print_header("离线依赖检查")

    if not os.path.isdir(PYLIB_DIR):
        print(f"[FAIL] pylib_py37/ 目录不存在: {PYLIB_DIR}")
        print("    请确保将 pylib_py37/ 目录完整复制到项目目录中")
        return False

    native_files = []
    for root, _dirs, files in os.walk(PYLIB_DIR):
        for filename in files:
            if filename.endswith((".pyd", ".so", ".dll", ".dylib")):
                native_files.append(os.path.join(root, filename))
    all_ok = True
    if native_files:
        print("[FAIL] pylib_py37/ 中存在平台相关二进制文件：")
        for native_file in native_files[:10]:
            print(f"    {native_file}")
        if len(native_files) > 10:
            print(f"    ... and {len(native_files) - 10} more")
        print("    离线包必须只包含纯 Python 文件，或使用目标 ARM64 架构构建")
        all_ok = False
    else:
        print("[PASS] pylib_py37/ 未发现平台相关二进制文件")

    # 统计已安装的包数量
    wheel_count = len([f for f in os.listdir(PYLIB_DIR) if f.endswith(".whl") or f.endswith(".egg-info") or f.endswith(".dist-info")])
    print(f"[INFO] pylib_py37/ 包含 {len(os.listdir(PYLIB_DIR))} 个条目")

    # 尝试导入关键包
    sys.path.insert(0, PYLIB_DIR)
    required = [
        ("fastapi", "FastAPI", "0.65.2"),
        ("uvicorn", "uvicorn", "0.14.0"),
        ("starlette", "Starlette", "0.14.2"),
        ("pydantic", "pydantic", "1.8.2"),
        ("click", "click", "8.1.7"),
        ("h11", "h11", "0.12.0"),
        ("websockets", "websockets", "11.0.3"),
        ("aiofiles", "aiofiles", "0.7.0"),
    ]
    for pkg_name, display_name, expected_version in required:
        try:
            module = importlib.import_module(pkg_name)
            actual_version = _installed_version(pkg_name, module)
            if actual_version != expected_version:
                print(
                    f"[FAIL] {display_name}=={actual_version} "
                    f"(需要 {expected_version})"
                )
                all_ok = False
            else:
                print(f"[PASS] {display_name}=={actual_version}")
        except (ImportError, SyntaxError, RuntimeError) as e:
            print(f"[FAIL] {display_name} —— {e}")
            all_ok = False

    syntax_errors = []
    for root, _dirs, files in os.walk(PYLIB_DIR):
        for filename in files:
            if not filename.endswith(".py"):
                continue
            path = os.path.join(root, filename)
            try:
                with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
                    source = f.read()
                if sys.version_info >= (3, 8):
                    ast.parse(source, filename=path, feature_version=(3, 7))
                else:
                    compile(source, path, "exec")
            except SyntaxError as exc:
                syntax_errors.append(f"{path}:{exc.lineno}: {exc.msg}")
    if syntax_errors:
        print("[FAIL] pylib_py37/ 包含 Python 3.7 无法解析的代码：")
        for error in syntax_errors[:10]:
            print(f"    {error}")
        all_ok = False
    else:
        print("[PASS] pylib_py37/ 通过 Python 3.7 语法检查")

    return all_ok


def check_frontend_assets() -> bool:
    """Check whether the frontend can run without internet access."""
    print()
    print_header("前端资源检查")

    index_html = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_html):
        print(f"[FAIL] 未找到前端页面: {index_html}")
        return False

    with open(index_html, "r", encoding="utf-8") as f:
        content = f.read()

    has_cdn = "unpkg.com" in content or "cdn.jsdelivr.net" in content
    if has_cdn:
        print("[WARN] index.html 仍引用 CDN 地址（unpkg.com / cdn.jsdelivr.net）")
        if (
            os.path.isfile(os.path.join(STATIC_VENDOR_DIR, "vue.global.prod.js"))
            and os.path.isfile(os.path.join(STATIC_VENDOR_DIR, "echarts.min.js"))
        ):
            print("    已在 static/vendor/ 找到离线文件，但 index.html 未使用")
            print("    自动修复：切换到本地 vendor 引用")
            _patch_index_html()
            return True
        else:
            print("    内网环境无法加载 CDN 资源，页面会白屏")
            return False

    print("[PASS] index.html 不引用公网 CDN")
    print("[PASS] 前端可在内网环境直接加载")
    return True


def _patch_index_html() -> None:
    """Patch index.html to use local vendor files instead of CDN."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.isfile(index_path):
        return
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    content = content.replace(
        "https://unpkg.com/vue@3/dist/vue.global.prod.js",
        "/static/vendor/vue.global.prod.js"
    )
    content = content.replace(
        "https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js",
        "/static/vendor/echarts.min.js"
    )
    if content != original:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("    index.html 已修复，CDN 引用 -> 本地 static/vendor/ 引用")
    else:
        print("    index.html 无需修复")


def find_log_file() -> tuple:
    """Find or create a log file. Returns (path, created)."""
    print()
    print_header("日志文件检查")

    # 优先级 1: 环境变量
    env_path = os.environ.get("LOG_FILE_PATH", "")
    if env_path and os.path.isfile(env_path):
        size = os.path.getsize(env_path)
        print(f"[PASS] LOG_FILE_PATH={env_path} ({size} bytes)")
        return env_path, False, 0

    # 优先级 2: /var/log/nginx/access.log
    nginx_path = "/var/log/nginx/access.log"
    if os.path.isfile(nginx_path):
        size = os.path.getsize(nginx_path)
        print(f"[PASS] 使用 {nginx_path} ({size} bytes)")
        return nginx_path, False, 0

    # 优先级 3: 项目目录下 sample_access.log
    sample_path = os.path.join(PROJECT_DIR, "sample_access.log")
    if os.path.isfile(sample_path):
        size = os.path.getsize(sample_path)
        print(f"[PASS] 使用样本日志: sample_access.log ({size} bytes)")
        return sample_path, False, 0

    # 优先级 4: 创建 test.log
    test_path = os.path.join(PROJECT_DIR, "test.log")
    _generate_sample_log(test_path)
    print(f"[INFO] 已创建测试日志: test.log (20 条模拟记录)")
    return test_path, True, 20


def _generate_sample_log(path: str) -> None:
    """Generate 20 sample Nginx combined-format log lines."""
    now = datetime.datetime.now()
    urls = ["/api/users", "/api/orders", "/api/products", "/api/search", "/api/auth"]
    methods = ["GET", "GET", "POST", "PUT", "DELETE"]
    statuses = [200, 200, 200, 200, 201, 204, 301, 401, 500, 500]
    agents = ["Mozilla/5.0", "curl/7.68.0", "python-requests/2.25.1"]

    lines = []
    for i in range(20):
        ts = now + datetime.timedelta(seconds=i * 2)
        time_str = ts.strftime("%d/%b/%Y:%H:%M:%S +0800")
        ip = f"192.168.1.{(i % 10) + 1}"
        url = urls[i % len(urls)]
        method = methods[i % len(methods)]
        status = statuses[i % len(statuses)]
        agent = agents[i % len(agents)]
        rt = round((i % 10 + 1) * 0.05 + i * 0.01, 3)
        body = (i + 1) * 50 + 100
        line = (
            f'{ip} - - [{time_str}] "{method} {url} HTTP/1.1" '
            f'{status} {body} "-" "{agent}" {rt}'
        )
        lines.append(line)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def find_free_port(start: int = 8000, max_attempts: int = 50) -> int:
    """Find the first available port starting from *start*."""
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    return 0


def check_port(preferred: int = 8000) -> int:
    """Check port availability and return usable port."""
    print()
    print_header("端口检查")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("0.0.0.0", preferred))
            print(f"[PASS] 端口 {preferred} 可用")
            return preferred
        except OSError:
            new_port = find_free_port(preferred + 1)
            if new_port:
                print(f"[WARN] 端口 {preferred} 被占用，改用 {new_port}")
            else:
                print(f"[FAIL] 未找到可用端口（从 {preferred} 开始）")
            return new_port


def generate_startup_command(log_path: str, port: int, deps_ok: bool) -> None:
    """Print the one-command startup command."""
    print()
    print_header("一键启动命令")

    if not deps_ok:
        print("  依赖检查未通过，请先修复依赖问题")
        return

    if port == 0:
        print("  无可用端口，请检查防火墙或已运行的服务")
        return

    print("  修改 start.sh 顶部的 Deployment configuration 后执行：")
    print("  chmod +x start.sh")
    print("  ./start.sh dashboard")
    print()
    print("  验证：浏览器访问 start.sh 中 DASHBOARD_PORT 配置的端口")


def main():
    print("=" * 54)
    print("  Nginx 日志性能监控 — 离线一键部署")
    print("  Python 3.7+ | 纯标准库 | 无需外网")
    print("=" * 54)

    check_python_version()
    check_stdlib()

    deps_ok = check_offline_deps()
    fe_ok = check_frontend_assets()
    log_path, created, count = find_log_file()
    port = check_port(8000)

    # Summary
    print()
    print_header("检查总结")
    print(f"  Python           : {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"  后端依赖         : {'OK' if deps_ok else 'FAIL'}")
    print(f"  前端资源         : {'OK' if fe_ok else 'FAIL'}")
    print(f"  日志文件         : {log_path}")
    if created:
        print(f"  模拟数据         : {count} 条")
    print(f"  监听端口         : {port}")

    # 如果前端资源缺失，尝试修复
    if not fe_ok:
        print()
        print_header("前端资源修复")
        print("  当前包的前端仍有外部依赖，请使用最新版 static/index.html")
        print("  或者在外网运行 python3 bundle_offline.py ./output 生成完整离线包")

    generate_startup_command(log_path, port, deps_ok)

    print()
    print("=" * 54)
    print("  deploy_offline.py 执行完毕")
    print("  如有问题请查阅 DEPLOY.md 中的「故障排查」章节")
    print("=" * 54)


if __name__ == "__main__":
    main()
