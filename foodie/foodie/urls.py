"""
URL configuration for foodie project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from foodapp import views  # Import the view

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('addfood/',views.displayfooditem, name='addfood'),
    path('food/',views.addfooditem, name='food'),
    path('menu/',views.getfooditem,name='menu'),
    path('food/update/<int:Id>/', views.updatefooditem, name='updatefood'),
    path('food/delete/<int:Id>/', views.deletefooditem, name='deletefood'),
    path('search/', views.fooditem_search, name='fooditem_search'),


    path('login/', views.login_view, name='login'),
    path('register/', views.register_customer, name='register'),
    path('logout/', views.logout_view, name='logout'), 
    path('logged_out/', views.logout_success, name='logout_success'),
    path('customers/', views.customer_list_view, name='customers'),


    
    path('cart/', views.view_cart, name='view_cart'),
    path('updateprice/<int:id>/<int:quantity>/<str:total>/', views.update_price, name='update_price'),
    path('add-to-cart/<int:Id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/delete/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),

    path('checkout/', views.checkout, name='checkout'),
    path('placeorder/', views.place_order, name='place_order'),
    
    

    path('razorpay/<int:order_id>/', views.create_razorpay_order, name='create_razorpay_order'),
    path("payment/success/", views.payment_success, name="payment_success"),
    path('orders/history/', views.order_history, name='order_history'),
    path('emailconfirmation/',views.send_confirmation_email, name='emailconfirmation'),
    
    
  
    


    

   

    
    
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)