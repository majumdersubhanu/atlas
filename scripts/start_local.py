"""Run Jupyter and the synthetic API with the Python selected by uv.

Both services stay on loopback. This process owns their lifetime: Ctrl-C stops
both services. Authentication URLs are saved only under ignored .runtime/.
"""

import argparse
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

from jupyter_server.serverapp import list_running_servers

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = {
    "01": "01_atlas_pipeline.ipynb",
    "02": "02_research_experiments.ipynb",
    "03": "03_real_data_defense.ipynb",
    "04": "04_visualization_comparison.ipynb",
    "05": "05_visualization_study_analysis.ipynb",
}


def port_available(port: int) -> bool:
    """Check by binding, including listeners not yet accepting requests."""
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jupyter-port", type=int, default=8888)
    parser.add_argument("--api-port", type=int, default=8000)
    parser.add_argument("--notebook", choices=NOTEBOOKS, default="04")
    args = parser.parse_args()
    ports = (args.jupyter_port, args.api_port)
    if len(set(ports)) != 2 or any(not 1 <= port <= 65535 for port in ports):
        parser.error("Choose two distinct ports between 1 and 65535")
    for port in ports:
        if not port_available(port):
            parser.error(f"Port {port} is occupied. Stop its owner or choose another port.")

    runtime = ROOT / ".runtime"
    runtime.mkdir(exist_ok=True)
    url_file = runtime / "jupyter_url.txt"
    url_file.unlink(missing_ok=True)
    commands = {
        "jupyter": [
            "-m",
            "jupyterlab",
            "--no-browser",
            "--ip=127.0.0.1",
            f"--port={args.jupyter_port}",
            "--ServerApp.port_retries=0",
            f"--ServerApp.root_dir={ROOT}",
        ],
        "api": ["-m", "uvicorn", "atlas.api:app", "--host", "127.0.0.1", "--port", str(args.api_port)],
    }
    children = []
    try:
        for name, command in commands.items():
            with (runtime / f"{name}.log").open("a", encoding="utf-8") as log:
                children.append(
                    subprocess.Popen(
                        [sys.executable, *command],
                        cwd=ROOT,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        start_new_session=os.name == "posix",
                    )
                )
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if any(child.poll() is not None for child in children):
                raise RuntimeError("A service exited; inspect .runtime/jupyter.log and api.log")
            servers = [
                server
                for server in list_running_servers()
                if server["port"] == args.jupyter_port and Path(server["root_dir"]).resolve() == ROOT
            ]
            if servers and not port_available(args.api_port):
                token = servers[0].get("token", "")
                if not token:
                    raise RuntimeError("Jupyter did not supply a token; inspect its authentication settings")
                url = (
                    f"http://127.0.0.1:{args.jupyter_port}/lab/tree/"
                    f"notebooks/{NOTEBOOKS[args.notebook]}?token={quote(token, safe='')}"
                )
                fd = os.open(url_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    handle.write(url)
                print(f"Notebook: {url}", flush=True)
                print(f"Dashboard: http://127.0.0.1:{args.api_port}/", flush=True)
                print(f"API: http://127.0.0.1:{args.api_port}/docs", flush=True)
                print("Ctrl-C stops both services. Logs: .runtime/", flush=True)
                break
            time.sleep(0.25)
        else:
            raise RuntimeError("Services did not become ready within 30 seconds; inspect .runtime logs")

        while all(child.poll() is None for child in children):
            time.sleep(0.5)
        raise RuntimeError("A service stopped unexpectedly; inspect .runtime logs")
    except KeyboardInterrupt:
        print("\nStopping Atlas services…")
    finally:
        # uv may forward the terminal interrupt after Python receives it directly.
        # Let cleanup finish even when a second interrupt arrives during wait().
        previous_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        try:
            for child in children:
                if child.poll() is None:
                    child.terminate()
            for child in children:
                try:
                    child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
        finally:
            url_file.unlink(missing_ok=True)
            signal.signal(signal.SIGINT, previous_handler)


if __name__ == "__main__":
    main()
