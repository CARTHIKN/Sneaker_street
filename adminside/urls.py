
from django.urls import path
from . import views
app_name = 'adminside'

urlpatterns = [
    path('', views.admin_login, name="adminlogin"),
    path('admin-logout/', views.admin_logout, name="admin-logout"),
    path('dashboard/', views.dashboard, name="dashboard"), 


    path('dashboard/show-product/', views.show_product, name="show-product"),
    path('dashboard/users-list/', views.users_list, name="users-list"),
    path('admin-users-block-unblock/<int:id>',views.admin_users_block_unblock, name = "admin-users-block-unblock"),
    path('dashboard/categories', views.categories, name="categories"),
    path('dashboard/add-product', views.add_product, name="add-product"),
    path('dashboard/orders', views.admin_orders, name="admin-orders"),

    path('soft-delete-category/<int:category_id>/', views.toggle_soft_delete, name='soft-delete-category'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit-product'),
    path('update-product/<int:product_id>/', views.update_product, name='update-product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete-product'),
    path('admin-orders-details/<int:order_number>', views.admin_orders_details, name='admin-orders-details'),
    path('delivered-order/<int:order_number>/', views.delivered_order, name='delivered-order'),
    path('adminadd_variations/', views.add_variations, name='add-variations'),
    path('adminadd_coupon/', views.add_coupon, name='add-coupon'),


    
]