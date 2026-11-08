from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_paymentlog_options_alter_transaction_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='provider',
            field=models.CharField(default='sandbox', max_length=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='failure_reason',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
