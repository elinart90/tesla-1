# VRA File Management System (VRA-FMS)
## Full System Documentation
### Volta River Authority – Ghana

---

## System Overview

The **VRA File Management System** is an enterprise web application built for the Volta River Authority (VRA) to manage the upload, retrieval, and monitoring of organizational files. It provides:

- **Centralized File Storage** with unique file IDs
- **Email & SMS Notifications** via Yagmail and Twilio
- **Automated 3-Day Reminders** using APScheduler
- **Power BI Analytics Dashboard** for reporting
- **Full Audit Trail** of all file operations

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Web Framework | Django 4.2 |
| Database | PostgreSQL 15+ |
| DB Driver | psycopg2-binary |
| Email | Yagmail (Gmail SMTP) |
| SMS | Twilio |
| Scheduler | APScheduler + django-apscheduler |
| Reporting | Microsoft Power BI Embed |
| Frontend | Django Templates + Vanilla JS |
| Charts | Chart.js (CDN) |
| Server | Gunicorn + Nginx (production) |

---

## Project Structure

```
vra_fms/
├── manage.py
├── requirements.txt
├── .env.example
├── setup_venv.sh
├── vra_fms/                 # Project configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── files/               # File management
│   │   ├── models.py        # ManagedFile, UserProfile, etc.
│   │   ├── views.py         # Upload, list, retrieve, delete
│   │   ├── forms.py         # Upload and search forms
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── signals.py       # Auto-create UserProfile
│   ├── notifications/       # Email & SMS
│   │   ├── models.py        # Notification log
│   │   ├── services.py      # EmailService, SMSService, NotificationService
│   │   ├── views.py
│   │   └── urls.py
│   ├── reminders/           # APScheduler reminders
│   │   ├── models.py        # FileReminder
│   │   ├── services.py      # ReminderService
│   │   ├── views.py
│   │   └── urls.py
│   └── dashboard/           # Stats + Power BI
│       ├── views.py
│       └── urls.py
├── templates/
│   ├── base/base.html       # Base layout with sidebar
│   ├── registration/login.html
│   ├── dashboard/
│   │   ├── dashboard.html
│   │   └── powerbi_report.html
│   ├── files/
│   │   ├── file_list.html
│   │   ├── file_upload.html
│   │   ├── file_detail.html
│   │   └── file_confirm_delete.html
│   ├── notifications/notification_list.html
│   └── reminders/reminder_list.html
├── static/
│   ├── css/main.css         # Full responsive CSS (no inline styles)
│   ├── js/
│   │   ├── main.js          # Sidebar, clock, alerts
│   │   ├── charts.js        # Chart.js dashboard charts
│   │   └── upload.js        # Drag-drop file upload
│   └── images/
├── media/                   # User-uploaded files
└── docs/
    ├── API_INTEGRATION_GUIDE.md
    ├── POWERBI_INTEGRATION_GUIDE.md
    ├── ENV_VARIABLES.md
    ├── process_model.svg
    └── schema_diagram.svg
```

---

## Installation

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip
- virtualenv

### 2. Clone / Extract Project

```bash
unzip vra_fms.zip -d vra_fms
cd vra_fms
```

### 3. Run Setup Script

```bash
chmod +x setup_venv.sh
bash setup_venv.sh
```

### 4.a Start Docker Desktop
docker compose up --build 
docker exec -it vra_django python manage.py createsuperuser
-- username 
-- email : mrnketia2904@gmail.com
-- password : wontumi@vra


### 4. Configure PostgreSQL

```sql
-- As postgres superuser:
-- USER USER CREDENTIALS 

CREATE DATABASE vra_fms_db;
CREATE USER wontumi WITH PASSWORD 'wontumi@vra';
GRANT ALL PRIVILEGES ON DATABASE vra_fms_db TO wontumi;
-- PostgreSQL 15+ also needs:
ALTER DATABASE vra_fms_db OWNER TO wontumi;
```

### 5. Configure Environment

```bash
cp .env.example .env
nano .env  # Fill in all required values
```

### 6. Run Migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 7. Create Initial File Categories


```bash
docker compose exec web python manage.py shell

>>> from apps.files.models import FileCategory
>>> FileCategory.objects.bulk_create([
...     FileCategory(name='Technical Reports', description='Engineering and technical documents'),
...     FileCategory(name='Administrative', description='Admin and HR documents'),
...     FileCategory(name='Financial', description='Invoices, budgets, financial statements'),
...     FileCategory(name='Projects', description='Project plans and deliverables'),
...     FileCategory(name='Correspondence', description='Letters and memos'),
... ])
```

### 8. Start Development Server

```bash
python manage.py runserver
```

Access at: http://127.0.0.1:8000/

---

## URL Routes

| URL | View | Description |
|-----|------|-------------|
| `/` | `file_list` | File repository |
| `/files/upload/` | `file_upload` | Upload a file |
| `/files/<pk>/` | `file_detail` | File details |
| `/files/<pk>/retrieve/` | `file_retrieve` | Download file + log |
| `/files/<pk>/delete/` | `file_delete` | Delete file |
| `/dashboard/` | `dashboard` | Statistics dashboard |
| `/dashboard/reports/` | `powerbi_report` | Power BI embed |
| `/notifications/` | `notification_list` | User notifications |
| `/reminders/` | `reminder_list` | User reminders |
| `/login/` | `LoginView` | Authentication |
| `/admin/` | Django Admin | Administration |

---

## System Flow

### File Upload
1. User submits upload form
2. System validates file type and size
3. Unique UUID `file_id` is generated
4. File metadata stored in `ManagedFile` table
5. APScheduler schedules 3-day reminder job
6. Yagmail + Twilio send upload confirmation

### File Retrieval
1. User requests file download
2. System checks file exists
3. File served as `FileResponse` download
4. `FileRetrievalLog` record created
5. File status updated to `retrieved`
6. Retrieval notification sent via email + SMS

### 3-Day Reminder
1. APScheduler fires `send_reminder_job` function
2. System checks if file is still `uploaded` (not retrieved)
3. If not retrieved: sends reminder via Yagmail + Twilio
4. `FileReminder.status` updated to `sent` or `skipped`

---

## Production Deployment

### Gunicorn + Nginx

```bash
# Install
pip install gunicorn

# Run
gunicorn vra_fms.wsgi:application --workers 3 --bind 0.0.0.0:8000

# Nginx config (example)
server {
    listen 80;
    server_name vra-fms.vra.com.gh;

    location /static/ {
        alias /path/to/vra_fms/staticfiles/;
    }

    location /media/ {
        alias /path/to/vra_fms/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Security Considerations

- Set `DJANGO_DEBUG=False` in production
- Use HTTPS (Let's Encrypt / SSL certificate)
- Keep `.env` out of version control
- Rotate credentials regularly
- Set `FILE_UPLOAD_MAX_MEMORY_SIZE` appropriately
- Enable Django's CSRF protection (already enabled)

---

*VRA File Management System Documentation*  
*Volta River Authority, Accra, Ghana*
