
from django.urls import path
from . import views
from adminside.views import dashboard
app_name = 'adminside'

urlpatterns = [
    path('admin-login/', views.admin_login, name="admin-login"),
    path('admin-logout/', views.admin_logout, name="admin-logout"),
    path('dashboard/',views.dashboard, name="dashboard"),


    path('dashboard/show-product/', views.show_product, name="show-product"),
    path('dashboard/users-list/', views.users_list, name="users-list"),
    path('admin-users-block-unblock/<int:id>',views.admin_users_block_unblock, name = "admin-users-block-unblock"),
    path('dashboard/categories', views.categories, name="categories"),
    path('dashboard/add-product', views.add_product, name="add-product"),

    path('soft-delete-category/<int:category_id>/', views.toggle_soft_delete, name='soft-delete-category'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit-product'),
    path('update-product/<int:product_id>/', views.update_product, name='update-product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete-product'),


    
]