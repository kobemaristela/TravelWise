from django.db import models
from django.contrib.auth.models import User

# API Models
class TravelPlans(models.Model):
    name = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

        def __unicode__(self):
            return self.name


class Activities(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    link = models.TextField()
    note = models.TextField()
    activity = models.ForeignKey(TravelPlans, on_delete=models.CASCADE)


class Chat(models.Model):
    time = models.TimeField()
    user = models.TextField()
    msg = models.IntegerField()
    activity = models.ForeignKey(TravelPlans, on_delete=models.CASCADE)
