# Plain Django (5.2 LTS) + gunicorn + WhiteNoise

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

Open http://localhost:8000/admin/. Configuration is environment driven (see `.env.example`):
`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_DB_PATH`.
SQLite lives in the `django-data` volume mounted at `/data`.
