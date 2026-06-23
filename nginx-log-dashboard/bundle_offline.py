#!/usr/bin/env python3
"""Nginx Log Dashboard - Offline Bundle Generator

Usage:
    python3 bundle_offline.py /path/to/output_dir

生成一个完整的内网部署压缩包：
    output_dir/
    ├── nginx-log-dashboard/       # 项目代码
    └── nginx-log-dashboard-offline.zip
"""
import sys
import shutil
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent


def copy_project_files(output_dir: Path) -> None:
    """Copy project source files into a self-contained offline bundle."""
    target = output_dir / "nginx-log-dashboard"
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    exclude_dirs = {
        "__pycache__",
        ".git",
        "offline-packages",
        "node_modules",
        "pylib",
        "pylib-build",
        "watchfiles",
        "watchfiles-0.14.1.dist-info",
        "pylib-legacy",
        "dist",
    }
    exclude_files = {
        ".DS_Store",
        "Thumbs.db",
        "start_local.cmd",
        "local-server.log",
        "refresh-test.log",
        "run_server.py",
    }
    for item in PROJECT_DIR.iterdir():
        if item.name in exclude_dirs or item.name in exclude_files:
            continue
        if item.name.startswith("."):
            continue
        dst = target / item.name
        if item.is_dir():
            shutil.copytree(
                str(item),
                str(dst),
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                    ".git",
                    "*.pyd",
                    "*.dll",
                    "*.dylib",
                    "watchfiles",
                    "watchfiles-*.dist-info",
                ),
            )
        else:
            shutil.copy2(str(item), str(dst))
    print(f"[OK] Project files copied to {target}")


def create_archive(output_dir: Path) -> Path:
    """Create a zip/tar.gz archive of the bundle."""
    base_name = str(output_dir / "nginx-log-dashboard-offline")
    archive_name = shutil.make_archive(
        base_name,
        "zip",
        root_dir=str(output_dir),
        base_dir="nginx-log-dashboard",
    )
    print(f"[OK] Archive created: {archive_name}")
    return Path(archive_name)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bundle_offline.py /path/to/output_dir")
        sys.exit(1)
    output_dir = Path(sys.argv[1])
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Output directory: {output_dir}")
    copy_project_files(output_dir)
    archive = create_archive(output_dir)
    print()
    print("=" * 60)
    print("  Offline bundle ready!")
    print(f"  Archive: {archive}")
    print(f"  Size:    {archive.stat().st_size / 1024:.1f} KB")
    print("=" * 60)
    print()
    print("【内网部署步骤】")
    print("1. 将压缩包复制到内网机器")
    print("2. 解压后进入目录：")
    print(f"   cd nginx-log-dashboard/")
    print("3. 执行离线自检：")
    print("   python3 deploy_offline.py")
    print("4. 启动服务：")
    print("   vi start.sh  # 修改脚本顶部环境配置")
    print("   ./start.sh dashboard")
    print("5. Agent 节点修改并启动：")
    print("   vi start_agent.sh")
    print("   ./start_agent.sh")


if __name__ == "__main__":
    main()
