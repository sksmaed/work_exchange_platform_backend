# Auto-generated migration to add phone field to User
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_user_date_joined_user_first_name_user_last_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(default="", max_length=30, blank=True),
        ),
    ]
