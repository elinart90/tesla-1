"""
Reminder Service - APScheduler integration
Schedules and triggers 3-day file retrieval reminders
"""

import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)


def send_reminder_job(file_pk: int):
    """
    APScheduler job function.
    Called 3 days after file upload if file hasn't been retrieved.
    """
    from apps.files.models import ManagedFile
    from apps.notifications.services import NotificationService
    from .models import FileReminder

    try:
        managed_file = ManagedFile.objects.get(pk=file_pk, is_active=True)
        reminder = FileReminder.objects.get(file=managed_file)
        reminder.triggered_at = timezone.now()

        if managed_file.status == 'retrieved':
            reminder.status = 'skipped'
            reminder.save()
            logger.info(f"Reminder skipped for {managed_file.file_name} – already retrieved.")
            return

        # Send the reminder
        NotificationService.send_reminder(managed_file)
        reminder.status = 'sent'
        reminder.save()
        logger.info(f"Reminder sent for {managed_file.file_name}")

    except Exception as e:
        logger.error(f"Reminder job failed for file_pk={file_pk}: {e}")


class ReminderService:
    """Manages scheduling of file reminders using APScheduler"""

    @staticmethod
    def get_scheduler():
        """Get or create APScheduler instance"""
        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore

        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        return scheduler

    @classmethod
    def schedule_file_reminder(cls, managed_file):
        """Schedule a reminder 3 days after file upload"""
        from .models import FileReminder
        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore

        reminder_days = getattr(settings, 'REMINDER_DAYS', 3)
        run_time = managed_file.upload_date + timedelta(days=reminder_days)

        # Create reminder record
        reminder, created = FileReminder.objects.get_or_create(
            file=managed_file,
            defaults={
                'scheduled_for': run_time,
                'status': 'scheduled',
            }
        )

        if not created:
            return reminder

        # Schedule the APScheduler job
        try:
            scheduler = BackgroundScheduler()
            scheduler.add_jobstore(DjangoJobStore(), "default")
            job_id = f"file_reminder_{managed_file.pk}"

            scheduler.add_job(
                send_reminder_job,
                'date',
                run_date=run_time,
                args=[managed_file.pk],
                id=job_id,
                replace_existing=True,
                jobstore='default',
            )

            if not scheduler.running:
                scheduler.start()

            reminder.job_id = job_id
            reminder.save()
            logger.info(f"Reminder scheduled for file {managed_file.file_name} at {run_time}")

        except Exception as e:
            logger.error(f"Failed to schedule reminder for {managed_file.file_name}: {e}")

        return reminder

    @classmethod
    def start_scheduler(cls):
        """Start the background scheduler on app startup"""
        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore

        try:
            scheduler = BackgroundScheduler()
            scheduler.add_jobstore(DjangoJobStore(), "default")
            if not scheduler.running:
                scheduler.start()
                logger.info("APScheduler started.")
        except Exception as e:
            logger.error(f"Scheduler start failed: {e}")
