from django.contrib import admin
from .models import TravelPlan, Activity, ChatMessage

# Register your models here.
admin.site.register(TravelPlan)
admin.site.register(Activity)
admin.site.register(ChatMessage)
