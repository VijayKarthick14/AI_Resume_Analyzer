from django.db import models

class Resume(models.Model):
    resume_file = models.FileField(upload_to='uploads/')