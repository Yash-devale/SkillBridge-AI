"""Start the Streamlit app and verify its health endpoint for CI smoke testing."""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> int:
    port = free_port()
    env = os.environ.copy()
    env.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
    command = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.address=127.0.0.1", f"--server.port={port}",
        "--server.headless=true", "--browser.gatherUsageStats=false",
    ]
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, env=env,
    )
    url = f"http://127.0.0.1:{port}/_stcore/health"
    deadline = time.monotonic() + 45
    try:
        while time.monotonic() < deadline:
            if process.poll() is not None:
                output = process.stdout.read() if process.stdout else ""
                print(output)
                raise RuntimeError(f"Streamlit exited early with code {process.returncode}")
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    body = response.read().decode("utf-8", errors="replace").strip()
                    if response.status == 200 and body.lower() == "ok":
                        print(f"Smoke test passed: {url} returned HTTP 200 / {body!r}")
                        return 0
            except (urllib.error.URLError, TimeoutError, OSError):
                time.sleep(0.5)
        output = process.stdout.read() if process.stdout else ""
        print(output)
        raise TimeoutError(f"Health endpoint did not become ready: {url}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
