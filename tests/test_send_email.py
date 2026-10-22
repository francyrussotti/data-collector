import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("send_email", ROOT / "scripts" / "send_email.py")
se = importlib.util.module_from_spec(spec)
spec.loader.exec_module(se)


def write(tmp_path, **kw):
    d = {"subject": "Radar · prova · 23 ott", "html": "<p>ciao</p>", "text": "ciao", **kw}
    p = tmp_path / "n.json"
    p.write_text(json.dumps(d))
    return p


def test_build_message(tmp_path):
    m = se.build(write(tmp_path), "jobnewsletter.fra@example.com", ["a@example.com"])
    assert m["To"] == "a@example.com"
    assert "jobnewsletter.fra@example.com" in m["From"]
    assert m.is_multipart() and m.get_body(("html",)).get_content().strip() == "<p>ciao</p>"


def test_rejects_placeholders_and_missing(tmp_path):
    with pytest.raises(ValueError):
        se.build(write(tmp_path, html="<p>{{titolo}}</p>"), "s@example.com", ["a@example.com"])
    with pytest.raises(ValueError):
        se.build(write(tmp_path, text=""), "s@example.com", ["a@example.com"])


def test_main_sends_via_smtp(tmp_path, monkeypatch):
    sent = []

    class FakeSMTP:
        def __init__(self, host, port, context=None, timeout=None):
            assert (host, port) == ("smtp.gmail.com", 465)
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False
        esmtp_features = {"auth": "LOGIN PLAIN"}
        def ehlo_or_helo_if_needed(self):
            pass
        def login(self, u, p):
            assert (u, p) == ("s@example.com", "app-pass")
        def send_message(self, m):
            sent.append(m)

    monkeypatch.setattr(se.smtplib, "SMTP_SSL", FakeSMTP)
    monkeypatch.setenv("SMTP_USER", "s@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", " app- pass ")
    monkeypatch.setenv("NEWSLETTER_TO", "a@example.com, b@example.com")
    assert se.main([str(write(tmp_path))]) == 0
    assert sent and sent[0]["To"] == "a@example.com, b@example.com"


def test_main_without_secrets(tmp_path, monkeypatch):
    monkeypatch.delenv("SMTP_USER", raising=False)
    monkeypatch.delenv("SMTP_PASSWORD", raising=False)
    assert se.main([str(write(tmp_path))]) == 2
