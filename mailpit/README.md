# Mailpit

A fake SMTP server with a web UI and REST API. Every message your app sends is captured and shown in the browser instead of being delivered, which makes it the standard "catch-all inbox" for local development. Works with the Django, Flask, Airflow, WordPress, Keycloak and Gitea templates in this repo.

## Run

```bash
cd mailpit
# Optional: copy .env.example to .env to override defaults
docker compose up -d --wait
```

- Web UI and API: http://localhost:8025
- SMTP: `localhost:1025` (no TLS, any username/password accepted)

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `MAILPIT_VERSION` | `v1.33.1` | Image tag |
| `MAILPIT_SMTP_PORT` | `1025` | Host SMTP port |
| `MAILPIT_UI_PORT` | `8025` | Host UI/API port |
| `MP_MAX_MESSAGES` | `5000` | Messages kept before the oldest are pruned |
| `MP_SMTP_AUTH_ACCEPT_ANY` | `1` | Accept any SMTP login |
| `MP_SMTP_AUTH_ALLOW_INSECURE` | `1` | Allow SMTP auth without TLS |
| `TZ` | `UTC` | Timezone for displayed times |

Messages persist in the `mailpit-data` volume. `docker compose down -v` clears them.

## Send a test message

```bash
python3 - <<'PY'
import smtplib
from email.message import EmailMessage
m = EmailMessage()
m["From"], m["To"], m["Subject"] = "me@example.test", "you@example.test", "Hello"
m.set_content("It works")
with smtplib.SMTP("localhost", 1025) as s:
    s.send_message(m)
PY
curl -s http://localhost:8025/api/v1/messages
```

## Use it from other containers

Attach your app to this stack's network (or run it in the same compose file) and point it at `mailpit:1025`. From the host use `localhost:1025`. Typical settings:

| Framework | Settings |
|---|---|
| Django | `EMAIL_HOST=localhost`, `EMAIL_PORT=1025`, `EMAIL_USE_TLS=False` |
| Airflow | `AIRFLOW__SMTP__SMTP_HOST=mailpit`, `AIRFLOW__SMTP__SMTP_PORT=1025`, `AIRFLOW__SMTP__SMTP_STARTTLS=False`, `AIRFLOW__SMTP__SMTP_SSL=False` |
| WordPress | an SMTP plugin pointed at `mailpit:1025` |

## Resources

- https://mailpit.axllent.org/docs/
- https://github.com/axllent/mailpit
