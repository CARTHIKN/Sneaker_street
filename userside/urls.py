from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name="landing"),
    path('user_login', views.user_login, name ="user_login"),
    path('signup', views.signup, name ="signup"),
    path('signout', views.signout, name ="signout"),

    path('verify_otp', views.verify_otp, name ="verify_otp"),
    path('shop-product/', views.shop_product, name='shop-product'),
    path('shop-product/<str:att>', views.shop_product, name='shop-product'),
    path('shop/category/<slug:category_slug>/', views.shop_product_by_category, name='shop-product-by-category'),

    path('product/<int:product_id>/', views.product_details, name='product_details'),
    path('search/', views.search, name ="search"),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('password_verify_otp', views.password_verify_otp, name ="password-verify-otp"),
    path('reset-Password/', views.reset_password, name='reset-Password'),
    # path('filter-by/', views.filters, name='filters'),

    
]       