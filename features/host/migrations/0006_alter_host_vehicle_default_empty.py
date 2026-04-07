from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("host", "0005_hostreviewimage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="host",
            name="vehicle",
            field=models.CharField(
                blank=True,
                default="",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="host",
            name="allowance",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
    ]
