from django.urls import path
from . import views
app_name = 'userprofile'

urlpatterns = [
    
    path('user-profile/', views.user_profile, name="user-profile"),
    path('edit-profile/', views.edit_profile, name='edit-profile'),
    path('change_Password/', views.change_password, name='change-password'),
    path('user-orders/', views.user_orders, name='user-orders'),
    path('user-address/', views.user_address, name='user-address'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit-address'),
    path('user-add-address/', views.user_add_address, name='user-add-address'),
    


 

]