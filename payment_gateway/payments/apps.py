from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments"

    def ready(self):
        from django.db.models.signals import post_migrate

        def seed_after_migrate(sender, **kwargs):
            if getattr(sender, 'name', None) != 'payments':
                return
            from payments.seed import seed_demo_user
            seed_demo_user()

        post_migrate.connect(seed_after_migrate, dispatch_uid='payments-seed-demo')
