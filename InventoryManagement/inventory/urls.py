from . import views
from django.urls import path

app_name = "inventory"

urlpatterns = [
    path('',views.index, name = 'index'),
    path('category/', views.category, name='category'),
    path('manage-cat', views.manage_category, name='manage-category'),
    path('save-cat/', views.save_category, name='save-category'),
    path('delete-cat/', views.delete_category, name='delete-category'),
    path('product/', views.product,name='product'),
    path('manage-prod/', views.manage_product, name='manage-product'),
    path('save-prod/', views.save_product, name='save-product'),
    path('delete-prod/', views.delete_product, name='delete-product'),
    path('about', views.about, name='about'),
    path('update/<int:pk>/', views.update_product,name='update-product'),
    path('report_stock_issue/', views.report_stock_issue, name='report_stock_issue'),
    path('page/<int:pk>/', views.prodcut_page, name='product-page'),
    path('inventory/', views.inventory,name='inventory-map'),
    path('<int:pk>/<int:row_id>/', views.show_inventory_layout, name='show_inventory_layout'),
    path('<int:pk>/<int:row_id>/<int:column_id>/', views.show_column_layout, name='show_column_layout'),
]