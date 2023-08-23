from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name="landing"),
    path('home/', views.home, name="home"),
    path('register/', views.register, name="register"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),

    path('create/', views.create_plan, name="create-plan"),
    path('my_plans/', views.history_view, name="history"),
]
