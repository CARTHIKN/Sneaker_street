from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name="landing"),
    path('user_login', views.user_login, name ="user_login"),
    path('signup', views.signup, name ="signup"),
    path('signout', views.signout, name ="signout"),
    
]