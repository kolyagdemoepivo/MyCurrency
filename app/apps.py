from django.apps import AppConfig
import logging

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    
    def ready(self):
        try:
            from app.management.commands.start_scheduler import scheduler
            scheduler.start()
        except:
            logging.info("The scheduler has already been started.")