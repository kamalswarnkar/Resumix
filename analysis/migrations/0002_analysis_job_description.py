from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("analysis", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="analysis",
            name="job_description",
            field=models.TextField(blank=True),
        ),
    ]
