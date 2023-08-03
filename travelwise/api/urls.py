from django.urls import path, include, re_path
from api import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    re_path(r'^validateUser/(?P<username>\w{1,50})/$', views.validateUser, name='validateUser'),
]