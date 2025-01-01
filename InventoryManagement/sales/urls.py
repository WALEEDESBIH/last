from . import views
from django.urls import path

app_name = "sales"

urlpatterns = [
    path('sales-list/', views.sales_list, name='sales-list'),
    path('receipt', views.receipt, name='receipt'),
    path('delete-sale', views.delete_sale, name='delete-sale'),
    path('orders/', views.order_list, name='order-list'),
    path('seen/',views.mark_orders_as_seen, name='seen' ),
    path('details/<int:pk>/', views.order_details, name='order-details'),
    
]