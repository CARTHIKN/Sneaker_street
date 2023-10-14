from django.urls import path
from . import views
app_name = 'userprofile'

urlpatterns = [
    path('user-profile/', views.user_profile, name="user-profile"),
    path('edit-profile/', views.edit_profile, name='edit-profile')
 

]