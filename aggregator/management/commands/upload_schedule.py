from django.core.management.base import BaseCommand
from aggregator.schedule_io import upload_schedule, generate_report, generate_prs
from datetime import datetime
import logging
import pathlib

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Parse balance components and insert to DB IEQ if component 2 or cons-gen if component 1'

    def handle(self, *args, **options):
        file = pathlib.Path('/Users/tritaer/Downloads/graph.xlsx')
        # upload_schedule(file)
        # generate_report(datetime(2025, 8, 27))
        generate_prs(datetime(2025, 8, 27))
