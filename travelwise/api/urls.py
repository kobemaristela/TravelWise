from django.urls import path, include
from api import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('plan/', views.plan, name='plan'),
]