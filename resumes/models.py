from django.db import models


class Resume(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="resumes", db_index=True)
    file = models.FileField(upload_to="resumes/%Y/%m/%d/")
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Resume {self.id} - {self.user.email}"
