from django.urls import path
from . import views


urlpatterns = [
  path('wallet/', views.wallet, name='wallet'),
  path("getwallet_total", views.get_wallet_grand_total, name="get_wallet_grand_total"),

]