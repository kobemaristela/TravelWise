from django.db import models
from django.contrib.auth.models import User

# API Models
class TravelPlan(models.Model):
    name = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    completed = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_modified']

        def __unicode__(self):
            return self.name


class Activity(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    link = models.URLField(null=True)
    note = models.TextField(null=True)
    plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE)


class ChatMessage(models.Model):
    time = models.TimeField()
    user = models.TextField()
    msg = models.TextField()
    function_name = models.CharField(max_length=100, blank=True, default='')
    plan = models.ForeignKey(TravelPlan, on_delete=models.CASCADE)
