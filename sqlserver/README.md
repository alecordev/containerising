# Microsoft SQL Server

SQL Server 2025 on Linux (Developer edition): `mcr.microsoft.com/mssql/server:2025-CU9-GDR1-ubuntu-24.04`.

```bash
# optional: copy .env.example to .env to override defaults
docker compose up -d --wait     # first start takes ~30-60 seconds
docker compose down             # add -v to delete data
```

> **Licence**: the container needs `ACCEPT_EULA=Y` (set by default in this template). By setting it you accept the [SQL Server licence terms](https://go.microsoft.com/fwlink/?linkid=857698). The **Developer** edition is free for development and testing, **not** for production.

## Access

| What | Value |
|---|---|
| Host / port | `localhost:1433` |
| Login | `sa` / `Str0ng!Passw0rd` |

```bash
docker compose exec sqlserver /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa   # prompts for the password
```

```sql
CREATE DATABASE demo;
GO
SELECT @@VERSION;
GO
```

Connection strings:

- ADO.NET / JDBC: `Server=localhost,1433;User Id=sa;Password=Str0ng!Passw0rd;TrustServerCertificate=True`
- SQLAlchemy: `mssql+pyodbc://sa:Str0ng%21Passw0rd@localhost:1433/master?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes`

## Environment variables

| Variable | Default |
|---|---|
| `MSSQL_VERSION` | `2025-CU9-GDR1-ubuntu-24.04` |
| `ACCEPT_EULA` | `Y` |
| `MSSQL_PID` | `Developer` |
| `MSSQL_SA_PASSWORD` | `Str0ng!Passw0rd` (8+ chars; upper, lower, digit, symbol) |
| `MSSQL_MEMORY_LIMIT_MB` | `2048` |
| `MSSQL_AGENT_ENABLED` | `false` |
| `MSSQL_PORT` | `1433` |
| `TZ` | `UTC` |

## Notes

- **RAM**: SQL Server needs at least 2 GB; Docker Desktop must have that available.
- **Architecture**: x86-64 image. On Apple Silicon it runs under emulation (Rosetta/QEMU) and can be slow or unstable.
- `sqlcmd` is `/opt/mssql-tools18/bin/sqlcmd`; the old `/opt/mssql-tools` path is gone, and `-C` is needed to trust the self-signed certificate.
- The SA password is set on the first start only; `docker compose down -v` to reset. If the password is too weak the container exits immediately (check `docker compose logs`).
- Data lives in the named volume `sqlserver-data`.

## Resources

- https://learn.microsoft.com/sql/linux/quickstart-install-connect-docker
- https://hub.docker.com/r/microsoft/mssql-server

## Smoke test

`python scripts/smoke.py sqlserver` starts this stack, waits for the healthchecks, runs [`smoke.py`](smoke.py) (a real round trip against the service) and tears everything down again. `smoke.py` is also a runnable example: with the stack already up, `python smoke.py` (or `uv run smoke.py`) runs just the check (from another directory give the path, e.g. `uv run sqlserver/smoke.py`); it needs only the Python standard library.
