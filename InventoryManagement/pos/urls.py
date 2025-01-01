from . import views
from django.urls import path

app_name = "pos"

urlpatterns = [
    path('pointofsale/', views.pos, name='pos'),
    path('check-modal', views.checkout_modal, name='checkout'),
    path('save/', views.save_pos, name='save-pos'),
    path('inbound/', views.inbound, name='inbound'),
    path('saleorder/<int:pk>/', views.saleorder, name="saleorder"),
    path('<int:pk>/confirm-order/', views.confirm_order, name="confirm-order"),
]