from django.db import models
from django.contrib.auth.models import User


class CVAnalysis(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    cv_text = models.TextField(blank=True)
    job_description = models.TextField(blank=True)

    match_score = models.IntegerField()
    summary = models.TextField()

    strengths = models.TextField(blank=True)
    missing_skills = models.TextField(blank=True)
    improvements = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.match_score}%"