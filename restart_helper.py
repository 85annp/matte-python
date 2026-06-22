import os
import socket
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HOST = "127.0.0.1"
PORT = 8000


def port_in_use() -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)
    try:
        sock.connect((HOST, PORT))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def main():
    deadline = time.time() + 10
    while time.time() < deadline:
        if not port_in_use():
            subprocess.Popen(
                [sys.executable, os.path.abspath(os.path.join(BASE_DIR, "main.py"))],
                cwd=BASE_DIR,
                stdout=None,
                stderr=None,
                stdin=None,
            )
            return
        time.sleep(0.2)

    raise SystemExit(1)


if __name__ == "__main__":
    main()
