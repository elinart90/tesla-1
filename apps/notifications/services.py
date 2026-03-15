"""
Notification Service - handles Email (Yagmail) and SMS (Twilio)
Volta River Authority File Management System
"""

import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class EmailService:
    """Email notifications using Yagmail (Gmail SMTP)"""

    @staticmethod
    def send(to_email: str, subject: str, body: str) -> bool:
        """
        Send email via Yagmail.
        Requires: YAGMAIL_USER and YAGMAIL_PASSWORD in settings/env.
        """
        try:
            import yagmail
            yag = yagmail.SMTP(
                user=settings.YAGMAIL_USER,
                password=settings.YAGMAIL_PASSWORD
            )
            yag.send(to=to_email, subject=subject, contents=body)
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Email send failed to {to_email}: {e}")
            return False


class SMSService:
    """SMS notifications using Twilio"""

    @staticmethod
    def send(to_phone: str, message: str) -> bool:
        """
        Send SMS via Twilio.
        Requires: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
        """
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            msg = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            logger.info(f"SMS sent to {to_phone}: SID={msg.sid}")
            return True
        except Exception as e:
            logger.error(f"SMS send failed to {to_phone}: {e}")
            return False


class NotificationService:
    """High-level notification orchestrator"""

    @staticmethod
    def _get_profile(user):
        """Safely get user profile"""
        try:
            return user.profile
        except Exception:
            return None

    @classmethod
    def send_upload_confirmation(cls, managed_file, user):
        """Notify user after successful file upload"""
        from .models import Notification
        profile = cls._get_profile(user)

        subject = f"[VRA-FMS] File Upload Confirmed – {managed_file.file_name}"
        body = f"""
Dear {user.get_full_name() or user.username},

Your file has been successfully uploaded to the VRA File Management System.

File Details:
  • File Name   : {managed_file.file_name}
  • File ID     : {managed_file.short_id}
  • Upload Date : {managed_file.upload_date.strftime('%d %B %Y, %H:%M')}
  • File Size   : {managed_file.file_size_display()}

Please keep your File ID for future reference.

Note: A reminder will be sent in 3 days if the file has not been retrieved.

Regards,
VRA File Management System
Volta River Authority
"""
        sms_body = f"[VRA-FMS] File '{managed_file.file_name}' (ID: {managed_file.short_id}) uploaded successfully on {managed_file.upload_date.strftime('%d/%m/%Y')}."

        notif = Notification.objects.create(
            user=user,
            file=managed_file,
            notification_type='upload_confirm',
            channel='both',
            subject=subject,
            message=body,
            status='pending',
        )

        email_ok = False
        sms_ok = False

        if profile and profile.receive_email and user.email:
            email_ok = EmailService.send(user.email, subject, body)

        if profile and profile.receive_sms and profile.phone_number:
            sms_ok = SMSService.send(profile.phone_number, sms_body)

        notif.status = 'sent' if (email_ok or sms_ok) else 'failed'
        notif.sent_at = timezone.now() if notif.status == 'sent' else None
        notif.save()
        return notif

    @classmethod
    def send_retrieval_notification(cls, managed_file, user):
        """Notify user when file is retrieved"""
        from .models import Notification
        profile = cls._get_profile(user)

        subject = f"[VRA-FMS] File Retrieved – {managed_file.file_name}"
        body = f"""
Dear {user.get_full_name() or user.username},

The following file has been successfully retrieved from the VRA File Management System.

File Details:
  • File Name     : {managed_file.file_name}
  • File ID       : {managed_file.short_id}
  • Retrieved On  : {timezone.now().strftime('%d %B %Y, %H:%M')}
  • Retrieved By  : {user.get_full_name() or user.username}

If you did not initiate this retrieval, please contact your system administrator immediately.

Regards,
VRA File Management System
Volta River Authority
"""
        sms_body = f"[VRA-FMS] File '{managed_file.file_name}' retrieved by {user.username} on {timezone.now().strftime('%d/%m/%Y %H:%M')}."

        notif = Notification.objects.create(
            user=user,
            file=managed_file,
            notification_type='retrieval',
            channel='both',
            subject=subject,
            message=body,
            status='pending',
        )

        email_ok = False
        sms_ok = False

        if profile and profile.receive_email and user.email:
            email_ok = EmailService.send(user.email, subject, body)

        if profile and profile.receive_sms and profile.phone_number:
            sms_ok = SMSService.send(profile.phone_number, sms_body)

        notif.status = 'sent' if (email_ok or sms_ok) else 'failed'
        notif.sent_at = timezone.now() if notif.status == 'sent' else None
        notif.save()
        return notif

    @classmethod
    def send_reminder(cls, managed_file):
        """Send 3-day reminder if file not yet retrieved"""
        from .models import Notification
        user = managed_file.uploaded_by
        profile = cls._get_profile(user)

        subject = f"[VRA-FMS] Reminder: File Not Retrieved – {managed_file.file_name}"
        body = f"""
Dear {user.get_full_name() or user.username},

This is a reminder that the following file you uploaded 3 days ago has not yet been retrieved.

File Details:
  • File Name    : {managed_file.file_name}
  • File ID      : {managed_file.short_id}
  • Upload Date  : {managed_file.upload_date.strftime('%d %B %Y, %H:%M')}
  • Status       : {managed_file.get_status_display()}

Please log in to the VRA File Management System to retrieve or review the file.

System URL: http://your-vra-domain.com/

Regards,
VRA File Management System
Volta River Authority
"""
        sms_body = f"[VRA-FMS] Reminder: File '{managed_file.file_name}' (ID: {managed_file.short_id}) uploaded 3 days ago has not been retrieved. Please log in to retrieve it."

        notif = Notification.objects.create(
            user=user,
            file=managed_file,
            notification_type='reminder',
            channel='both',
            subject=subject,
            message=body,
            status='pending',
        )

        email_ok = False
        sms_ok = False

        if profile and profile.receive_email and user.email:
            email_ok = EmailService.send(user.email, subject, body)

        if profile and profile.receive_sms and profile.phone_number:
            sms_ok = SMSService.send(profile.phone_number, sms_body)

        notif.status = 'sent' if (email_ok or sms_ok) else 'failed'
        notif.sent_at = timezone.now() if notif.status == 'sent' else None
        if notif.status == 'sent':
            managed_file.reminder_sent = True
            managed_file.reminder_sent_at = timezone.now()
            managed_file.save()
        notif.save()
        return notif
