# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///

"""Send a message over SMTP, then read it back through the HTTP API."""
import smtplib
from email.message import EmailMessage

import sys
from pathlib import Path

# Find scripts/ from any depth so this file also runs on its own (python smoke.py / uv run smoke.py)
sys.path.insert(0, str(next(p / "scripts" for p in Path(__file__).resolve().parents if (p / "scripts" / "smokelib.py").is_file())))
from smokelib import expect, http, port, retry, run, step  # noqa: E402

SUBJECT = "mailpit smoke test"


def main() -> None:
    step("send mail over SMTP")
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = "smoke@example.test", "dev@example.test", SUBJECT
    msg.set_content("hello from the smoke test")
    with smtplib.SMTP("localhost", port("MAILPIT_SMTP_PORT", 1025), timeout=10) as smtp:
        smtp.send_message(msg)

    step("read it back from the API")
    api = f"http://localhost:{port('MAILPIT_UI_PORT', 8025)}/api/v1/messages"
    retry(lambda: SUBJECT in http(api).body, timeout=20, interval=1, desc="message in Mailpit")
    expect(http(f"http://localhost:{port('MAILPIT_UI_PORT', 8025)}/").status == 200, "web UI not reachable")


run(main)
