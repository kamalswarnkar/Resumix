from django.db import models


class Analysis(models.Model):
    resume = models.ForeignKey("resumes.Resume", on_delete=models.CASCADE, related_name="analyses")
    match_score = models.FloatField(default=0.0, db_index=True)
    keyword_similarity = models.FloatField(default=0.0)
    skill_match_score = models.FloatField(default=0.0)
    experience_relevance = models.FloatField(default=0.0)
    ats_compliance = models.FloatField(default=0.0)
    skills_found = models.JSONField(default=list)
    skills_missing = models.JSONField(default=list)
    suggestions = models.TextField(blank=True)
    predicted_role = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis {self.id} - Resume {self.resume_id}"
