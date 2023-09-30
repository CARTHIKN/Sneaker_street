
from django.urls import path
from . import views

app_name = 'adminside'

urlpatterns = [
    path('admin/', views.adminlogin, name="adminlogin"),
    
]