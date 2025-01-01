from . import views
from django.urls import path

app_name = "e_commerce"

urlpatterns = [ 
    path('',views.Home,name='home'),
    path('base/',views.base,name='base'),
    path('products/',views.PRODUCT,name='product'),
    path('singleprod/<int:id>/',views.PRODUCT_DETAILS_PAGE,name='product_details'),
    path('search/',views.SEARCH,name='search'),
    path('contact/',views.CONTACT_US,name='contact'),
    path('register/',views.HandleRegister,name='register'),
    path('login/',views.HandleLogin,name='login'),
    path('logout/',views.HandleLogout,name='logout'),
    path('about/',views.ABOUT,name='about'),
    path('generate_pdf/<int:pk>/', views.generate_order_pdf, name='generate_order_pdf'),
    path('order-confirmation/<int:pk>/', views.order_confirmation, name='order_confirmation'),
    path('billing/<int:pk>/', views.billing, name='billing'),


    #cart
    path('cart/add/<int:id>/', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/',views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',views.item_decrement, name='item_decrement'),
    path('cart/cart_clear/', views.cart_clear, name='cart_clear'),
    path('cart/cart-detail/',views.cart_detail,name='cart_detail'),
    path('cart/checkout/',views.Check_out,name='checkout'),
    path('cart/checkout/placeorder',views.PLACE_ORDER,name='place_order'),
    
    
    ]