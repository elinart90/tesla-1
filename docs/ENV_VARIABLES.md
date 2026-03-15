# VRA File Management System
## Environment Variables Reference
### Volta River Authority

---

## Overview

All sensitive configuration for the VRA-FMS is managed through environment variables. Never hardcode credentials in source code. Use a `.env` file for local development and environment-level configuration in production.

---

## Variable Reference

### Django Core

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | ✅ Yes | None | Django secret key. Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_DEBUG` | No | `True` | Set to `False` in production |
| `ALLOWED_HOSTS` | ✅ Yes | `localhost,127.0.0.1` | Comma-separated list of allowed hostnames |

---

### PostgreSQL Database

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_NAME` | ✅ Yes | `vra_fms_db` | PostgreSQL database name |
| `DB_USER` | ✅ Yes | `vra_admin` | Database user |
| `DB_PASSWORD` | ✅ Yes | None | Database password |
| `DB_HOST` | No | `localhost` | Database host (use Docker container name if applicable) |
| `DB_PORT` | No | `5432` | PostgreSQL port |

---

### Email (Yagmail/Gmail SMTP)

| Variable | Required | Description |
|----------|----------|-------------|
| `YAGMAIL_USER` | ✅ Yes | Gmail address used to send emails |
| `YAGMAIL_PASSWORD` | ✅ Yes | Gmail App Password (16 characters) |
| `EMAIL_HOST_USER` | ✅ Yes | Same as YAGMAIL_USER (used by Django email backend) |
| `EMAIL_HOST_PASSWORD` | ✅ Yes | Same as YAGMAIL_PASSWORD |
| `DEFAULT_FROM_EMAIL` | No | `noreply@vra.com.gh` | From address shown in emails |

---

### Twilio SMS

| Variable | Required | Description |
|----------|----------|-------------|
| `TWILIO_ACCOUNT_SID` | ✅ Yes | Twilio Account SID (starts with `AC`) |
| `TWILIO_AUTH_TOKEN` | ✅ Yes | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | ✅ Yes | Your Twilio phone number in E.164 format (e.g. `+12345678901`) |

---

### Power BI

| Variable | Required | Description |
|----------|----------|-------------|
| `POWERBI_CLIENT_ID` | ✅ Yes | Azure AD App Registration Client ID |
| `POWERBI_CLIENT_SECRET` | ✅ Yes | Azure AD App Client Secret |
| `POWERBI_TENANT_ID` | ✅ Yes | Azure AD Tenant / Directory ID |
| `POWERBI_WORKSPACE_ID` | ✅ Yes | Power BI Workspace (Group) ID |
| `POWERBI_REPORT_ID` | ✅ Yes | Power BI Report ID |
| `POWERBI_DATASET_ID` | No | Power BI Dataset ID (for refresh triggers) |

---

### Application Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REMINDER_DAYS` | No | `3` | Days after upload before reminder is sent |

---

## Setting Up .env File

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit with your values
nano .env   # or vim .env

# 3. Verify Django can read the config
source venv/bin/activate
python manage.py check
```

---

## Loading .env in Django

The `settings.py` uses `os.environ.get()` directly. To automatically load `.env` on startup, install and configure `python-dotenv`:

```python
# At top of manage.py:
from dotenv import load_dotenv
load_dotenv()
```

Or in `settings.py`:
```python
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')
```

---

## Production Deployment Variables

For production (e.g., Ubuntu server with Gunicorn/Nginx):

```bash
# Set system-wide environment variables
sudo nano /etc/environment

# Or in systemd service file:
[Service]
Environment="DJANGO_SECRET_KEY=your-key"
Environment="DJANGO_DEBUG=False"
Environment="DB_PASSWORD=your-db-password"
```

---

## Security Notes

- Add `.env` to `.gitignore` — never commit it
- Use strong, randomly generated values for `DJANGO_SECRET_KEY`
- Rotate `POWERBI_CLIENT_SECRET` and `TWILIO_AUTH_TOKEN` annually
- In production, set `DJANGO_DEBUG=False` and configure `ALLOWED_HOSTS` properly

---

*VRA File Management System – Environment Variables Reference*  
*Volta River Authority, Ghana*
