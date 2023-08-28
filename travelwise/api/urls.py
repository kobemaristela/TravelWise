from django.urls import path, include, re_path
from api import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('plan/', views.plan, name='plan'),
    re_path(r'^validateUser/(?P<username>\w{1,50})/$', views.validateUser, name='validateUser'),
    re_path(r'^deletePlan/(?P<plan_id>\d{1,40})/$', views.delete_plan, name='deletePlan'),
    path('create_image/', views.create_image),
    path('plan/<int:plan_id>/activity/<int:activity_id>', views.update_plan_activity, name='updatePlanActivity'),
]