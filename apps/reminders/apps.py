from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reminders'
    verbose_name = 'Reminder System'

    def ready(self):
        """Start APScheduler when Django starts"""
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            from .services import ReminderService
            try:
                ReminderService.start_scheduler()
            except Exception:
                pass
