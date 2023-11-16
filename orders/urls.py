from django.urls import path
from . import views


urlpatterns = [
    path('order-summary/', views.order_summary, name='order-summary'),
    path('place-order/', views.place_order, name='place-order'),
    path('payment/payment-success', views.payment_success, name='payment-success'),
    path('payment/payment-failed/', views.payment_failed, name='payment-failed'),
    path('payment-success-page/', views.payment_success_page, name='payment-success-page'),
    path('user-order-details/<int:order_number>', views.user_order_details, name = 'user-order-details'),
    path('order-cancel-user/<int:order_number>', views.order_cancel_user, name='order-cancel-user'),
    path('add-address/', views.add_address, name='add-address'),
    path('default_address/<int:id>', views.default_address, name="default_address"),
    path('delete_address/<int:id>', views.delete_address, name="delete_address"),
    path('sales-report', views.sales_report, name='sales-report'),


    

]
