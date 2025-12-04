# Generated manually to remove UserProfile model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_auto_20251204_1147"),
    ]

    operations = [
        migrations.DeleteModel(
            name="UserProfile",
        ),
    ]
