"""Controls for presentation export and launcher preflight behavior."""

import runpy
import socket
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def test_offline_export_is_idempotent_and_preserves_embedded_figures():
    finalize = runpy.run_path(str(SCRIPTS / "finalize_presentation.py"))["finalize"]
    html = (
        '<html><head><script src="https://example.org/a.js"></script></head><body>'
        '$$E = A - L$$<img src="data:image/png;base64,ONE" alt="old">'
        '<img src="data:image/png;base64,TWO"/><img src="data:image/png;base64,THREE"></body></html>'
    )
    result = finalize(html)
    assert "<script" not in result
    assert "$$" not in result
    assert result.count('src="data:image/png;base64,') == 3
    assert result.count('alt="') == 3
    assert "E′ᵢ" in result
    assert finalize(result) == result
    with pytest.raises(ValueError, match="three figures"):
        finalize('<html><head></head><img src="unknown"></html>')


def test_launcher_rejects_occupied_port_before_starting_children(monkeypatch):
    launcher = runpy.run_path(str(SCRIPTS / "start_local.py"))
    with socket.socket() as occupied:
        occupied.bind(("127.0.0.1", 0))
        port = occupied.getsockname()[1]
        monkeypatch.setattr(sys, "argv", ["start_local.py", "--jupyter-port", str(port)])
        with pytest.raises(SystemExit) as error:
            launcher["main"]()
        assert error.value.code == 2
