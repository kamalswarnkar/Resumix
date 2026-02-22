from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("resumes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Analysis",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("match_score", models.FloatField(db_index=True, default=0.0)),
                ("keyword_similarity", models.FloatField(default=0.0)),
                ("skill_match_score", models.FloatField(default=0.0)),
                ("experience_relevance", models.FloatField(default=0.0)),
                ("ats_compliance", models.FloatField(default=0.0)),
                ("skills_found", models.JSONField(default=list)),
                ("skills_missing", models.JSONField(default=list)),
                ("suggestions", models.TextField(blank=True)),
                ("predicted_role", models.CharField(blank=True, max_length=100)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("resume", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="analyses", to="resumes.resume")),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
