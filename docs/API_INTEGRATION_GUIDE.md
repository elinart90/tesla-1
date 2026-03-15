# VRA File Management System
## External API Integration Guide
### Volta River Authority

---

## Table of Contents

1. [Email Integration (Yagmail + Gmail)](#1-email-integration)
2. [SMS Integration (Twilio)](#2-sms-integration-twilio)
3. [Power BI Integration](#3-power-bi-integration)

---

## 1. Email Integration (Yagmail + Gmail)

### Overview

The VRA-FMS uses **Yagmail** — a Gmail-focused Python email library — to send HTML/plain-text emails via Gmail's SMTP server. Emails are sent for:
- File upload confirmations
- File retrieval notifications
- 3-day reminder notifications

---

### Step 1: Create a Gmail Account (Dedicated)

Create a dedicated Gmail account for VRA notifications:  
Example: `vra-noreply@gmail.com`

> **Best Practice**: Do not use a personal Gmail account. Use a department-owned account.

---

### Step 2: Enable 2-Factor Authentication

1. Go to **Google Account → Security**
2. Enable **2-Step Verification**

This is required to generate App Passwords.

---

### Step 3: Create a Gmail App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in with your Gmail account
3. Under **Select app**, choose **Mail**
4. Under **Select device**, choose **Other (Custom name)** → type `VRA-FMS`
5. Click **Generate**
6. **Copy the 16-character App Password shown** (you won't see it again)

---

### Step 4: Configure Environment Variables

In your `.env` file:

```env
YAGMAIL_USER=vra-noreply@gmail.com
YAGMAIL_PASSWORD=xxxx xxxx xxxx xxxx   # 16-char App Password (spaces are OK)
DEFAULT_FROM_EMAIL=vra-noreply@gmail.com
```

---

### Step 5: Register Yagmail Credentials (One-Time)

Yagmail stores credentials in the OS keychain. For server deployments, use the environment variable approach (already implemented in `services.py`).

For local testing, run:

```bash
python manage.py shell
>>> import yagmail
>>> yagmail.register('vra-noreply@gmail.com', 'your-app-password')
```

---

### Step 6: Test Email Sending

```bash
python manage.py shell
>>> from apps.notifications.services import EmailService
>>> EmailService.send('test@example.com', 'VRA Test', 'Hello from VRA-FMS!')
True
```

---

### Gmail SMTP Settings Reference

| Setting          | Value                      |
|-----------------|----------------------------|
| SMTP Host       | smtp.gmail.com             |
| SMTP Port       | 587                        |
| TLS             | Yes                        |
| Authentication  | Gmail App Password         |

---

### Troubleshooting Email

| Error | Solution |
|-------|----------|
| `SMTPAuthenticationError` | Wrong App Password or 2FA not enabled |
| `Connection refused` | Port 587 blocked by firewall |
| `Less secure app access` | Use App Password instead |
| Emails going to spam | Add SPF/DKIM records to DNS |

---

## 2. SMS Integration (Twilio)

### Overview

The VRA-FMS uses **Twilio** to send SMS notifications to user phone numbers stored in their `UserProfile`. SMS messages are sent for the same events as email (upload, retrieval, reminders).

---

### Step 1: Create a Twilio Account

1. Go to: https://www.twilio.com/try-twilio
2. Register with your VRA email address
3. Verify your phone number

---

### Step 2: Get Your Credentials

From the **Twilio Console Dashboard** (https://console.twilio.com):

| Field             | Where to Find                     |
|-------------------|-----------------------------------|
| Account SID       | Dashboard → Account Info          |
| Auth Token        | Dashboard → Account Info (hidden) |
| Twilio Phone No.  | Phone Numbers → Manage → Active   |

---

### Step 3: Get a Twilio Phone Number

For Ghana (+233) SMS:
1. Console → **Phone Numbers → Manage → Buy a Number**
2. Filter by: **SMS capability**, Country: Ghana (if available)
3. Alternatively, use a US/UK number for international sending

> **Note**: Verify recipient numbers in trial accounts. Upgrade to a paid plan for production.

---

### Step 4: Configure Environment Variables

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+12345678901
```

---

### Step 5: Add User Phone Numbers

Each VRA staff member must have their phone number stored:

1. Admin → User Profiles → Select User → Add phone number in E.164 format
2. Example formats: `+233241234567` (Ghana), `+441234567890` (UK)

---

### Step 6: Test SMS Sending

```bash
python manage.py shell
>>> from apps.notifications.services import SMSService
>>> SMSService.send('+233241234567', 'VRA-FMS Test: Hello from VRA!')
True
```

---

### Twilio Trial Account Limitations

| Limitation | Description |
|-----------|-------------|
| Can only send to verified numbers | Add numbers at: Console → Verified Numbers |
| Messages include "Sent from your Twilio trial account" prefix | Upgrade to remove |
| $15.50 trial credit | Sufficient for hundreds of test messages |

---

### Ghana SMS Compliance

- Ensure you have user consent before sending SMS
- Include an opt-out mechanism: "Reply STOP to unsubscribe"
- The `receive_sms` flag in `UserProfile` handles opt-out preferences

---

### Troubleshooting SMS

| Error | Solution |
|-------|----------|
| `AuthenticationError` | Check Account SID and Auth Token |
| `Unverified number` | Add number to Trial verified list |
| `Invalid To phone number` | Ensure E.164 format (+233...) |
| SMS not received | Check Twilio logs at console.twilio.com |

---

## 3. Power BI Integration

See `POWERBI_INTEGRATION_GUIDE.md` for full Power BI documentation.

---

*VRA File Management System – API Integration Guide*  
*Volta River Authority, Ghana*
