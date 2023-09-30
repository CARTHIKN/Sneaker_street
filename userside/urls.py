from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name="landing"),
    path('user_login', views.user_login, name ="user_login"),
    path('signup', views.signup, name ="signup"),
    path('signout', views.signout, name ="signout"),
    path('verify_otp', views.verify_otp, name ="verify_otp"),
    path('product/<int:product_id>/', views.product_details, name='product_detail'),
    
]