from django.core.management.base import BaseCommand

from payments.seed import seed_demo_user
from payments.services import DEMO_EMAIL, DEMO_PASSWORD


class Command(BaseCommand):
    help = 'Create the demo merchant and a small set of sample payments.'

    def handle(self, *args, **options):
        user = seed_demo_user(force=True)
        if user is None:
            self.stdout.write('Demo user was not created. Sandbox mode or DEBUG is off.')
            return
        self.stdout.write(self.style.SUCCESS(
            f'Demo merchant ready: {DEMO_EMAIL} / {DEMO_PASSWORD}'
        ))
