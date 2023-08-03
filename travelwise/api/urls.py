from django.urls import path, include, re_path
from api import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('plan/', views.plan, name='plan'),
    re_path(r'^validateUser/(?P<username>\w{1,50})/$', views.validateUser, name='validateUser'),
]