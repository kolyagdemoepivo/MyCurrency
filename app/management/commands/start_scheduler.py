import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.core.management.base import BaseCommand

from app.jobs import fetching_provider_data

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):

    def handle(self, *args, **options):
        scheduler.add_job(
            fetching_provider_data,
            trigger=CronTrigger(minute="*/2"),
            id="fetching_provider_data_1",
            max_instances=1,
            replace_existing=True,
        )
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
