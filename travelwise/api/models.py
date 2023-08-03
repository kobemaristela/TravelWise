from django.db import models
from django.contrib.auth.models import User

# API Models
class TravelPlan(models.Model):
    name = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

        def __unicode__(self):
            return self.name


class Activity(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    link = models.TextField()
    note = models.TextField()
    plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE)


class ChatMessage(models.Model):
    time = models.TimeField()
    user = models.TextField()
    msg = models.TextField()
    plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE)
