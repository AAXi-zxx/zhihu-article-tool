# -*- coding: utf-8 -*-
"""AI知乎文章创作工具 - 一键启动脚本

双击 start_all.bat 运行，或直接 `python start_all.py`。
会自动按顺序启动：MySQL → Redis → 后端 → 前端，
已经运行的服务会自动跳过（通过端口检测）。

数据库与工具用绝对路径（devtools），前后端用相对路径（跟随本脚本所在目录）。
"""
import os
import socket
import subprocess
import time

# ============ 前后端路径（相对本脚本所在目录）============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# ============ 数据库与工具（绝对路径，换机器时改这里）============
MYSQL_EXE = r"C:\Users\10314\devtools\mysql-8.0.40-winx64\bin\mysqld.exe"
MYSQL_BASE = r"C:\Users\10314\devtools\mysql-8.0.40-winx64"
MYSQL_DATA = r"C:\Users\10314\devtools\mysql-8.0.40-winx64\data"
REDIS_EXE = r"C:\Users\10314\devtools\redis\redis-server.exe"
UV_EXE = r"C:\Users\10314\.local\bin\uv.exe"
NODE_EXE = r"C:\Users\10314\.workbuddy\binaries\node\versions\22.22.2-3\node.exe"

CREATE_NO_WINDOW = 0x08000000   # 后台运行（不弹窗）
CREATE_NEW_CONSOLE = 0x00000010  # 新控制台窗口（方便看日志）


def port_open(port: int) -> bool:
    """检测本地端口是否已被占用（同时检测 IPv4 和 IPv6）"""
    for host, family in (("127.0.0.1", socket.AF_INET), ("::1", socket.AF_INET6)):
        try:
            with socket.socket(family, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((host, port)) == 0:
                    return True
        except OSError:
            continue
    return False


def wait_port(port: int, timeout: int = 30) -> bool:
    """等待端口开始监听，最多 timeout 秒"""
    for _ in range(timeout):
        if port_open(port):
            return True
        time.sleep(1)
    return False


def main():
    print("=" * 48)
    print("  AI知乎文章创作工具 · 一键启动")
    print("=" * 48)

    # 1. MySQL
    if port_open(3306):
        print("[1/4] MySQL 已在运行，跳过")
    else:
        print("[1/4] 启动 MySQL ...")
        subprocess.Popen(
            [MYSQL_EXE, "--basedir=" + MYSQL_BASE,
             "--datadir=" + MYSQL_DATA, "--port=3306"],
            creationflags=CREATE_NO_WINDOW,
        )
        print("      MySQL 就绪" if wait_port(3306) else "      [警告] MySQL 启动超时")

    # 2. Redis
    if port_open(6379):
        print("[2/4] Redis 已在运行，跳过")
    else:
        print("[2/4] 启动 Redis ...")
        subprocess.Popen(
            [REDIS_EXE, "--port", "6379"],
            creationflags=CREATE_NO_WINDOW,
        )
        time.sleep(1)
        print("      Redis 就绪" if port_open(6379) else "      [警告] Redis 未就绪")

    # 3. 后端
    if port_open(8567):
        print("[3/4] 后端已在运行，跳过")
    else:
        print("[3/4] 启动后端（会弹出新窗口）...")
        subprocess.Popen(
            [UV_EXE, "run", "uvicorn", "app.main:app",
             "--host", "0.0.0.0", "--port", "8567"],
            cwd=BACKEND_DIR,
            creationflags=CREATE_NEW_CONSOLE,
        )
        print("      后端就绪" if wait_port(8567, 40) else "      [警告] 后端启动超时，请查看后端窗口")

    # 4. 前端
    if port_open(5173):
        print("[4/4] 前端已在运行，跳过")
    else:
        print("[4/4] 启动前端（会弹出新窗口）...")
        subprocess.Popen(
            [NODE_EXE, "node_modules/vite/bin/vite.js"],
            cwd=FRONTEND_DIR,
            creationflags=CREATE_NEW_CONSOLE,
        )
        print("      前端就绪" if wait_port(5173, 30) else "      [警告] 前端启动超时，请查看前端窗口")

    print("-" * 48)
    print("  前端页面 : http://localhost:5173/")
    print("  后端文档 : http://localhost:8567/docs")
    print("-" * 48)
    print("所有服务已启动：数据库在后台，前后端各有独立窗口。")
    print("本窗口 / PyCharm 可以关闭，不影响服务运行。")


if __name__ == "__main__":
    main()
