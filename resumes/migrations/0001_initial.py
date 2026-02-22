from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Resume",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="resumes/%Y/%m/%d/")),
                ("extracted_text", models.TextField(blank=True)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("user", models.ForeignKey(db_index=True, on_delete=django.db.models.deletion.CASCADE, related_name="resumes", to="users.user")),
            ],
            options={"ordering": ["-uploaded_at"]},
        ),
    ]
