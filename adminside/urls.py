
from django.urls import path
from . import views
from adminside.views import dashboard
app_name = 'adminside'

urlpatterns = [
    path('admin-login/', views.admin_login, name="admin-login"),
    path('dashboard/',views.dashboard, name="dashboard"),


    path('dashboard/show-product/', views.show_product, name="show-product"),
    path('dashboard/users-list/', views.users_list, name="users-list"),
    path('admin-users-block-unblock/<int:id>',views.admin_users_block_unblock, name = "admin-users-block-unblock"),
    path('dashboard/categories', views.categories, name="categories"),

    
]