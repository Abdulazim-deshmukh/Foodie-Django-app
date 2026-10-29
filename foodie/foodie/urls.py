"""
URL configuration for the Foodie project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from foodapp import views


urlpatterns = [

    # ============================================================
    # ADMIN
    # ============================================================

    path(
        "admin/",
        admin.site.urls,
    ),


    # ============================================================
    # HOME
    # ============================================================

    path(
        "",
        views.home,
        name="home",
    ),


    # ============================================================
    # FOOD MANAGEMENT
    # ============================================================

    path(
        "addfood/",
        views.displayfooditem,
        name="addfood",
    ),

    path(
        "food/",
        views.addfooditem,
        name="food",
    ),

    path(
        "menu/",
        views.getfooditem,
        name="menu",
    ),

    path(
        "food/update/<int:Id>/",
        views.updatefooditem,
        name="updatefood",
    ),

    path(
        "food/delete/<int:Id>/",
        views.deletefooditem,
        name="deletefood",
    ),

    path(
        "search/",
        views.fooditem_search,
        name="fooditem_search",
    ),


    # ============================================================
    # AUTHENTICATION
    # ============================================================

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "register/",
        views.register_customer,
        name="register",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "logged_out/",
        views.logout_success,
        name="logout_success",
    ),


    # ============================================================
    # CUSTOMERS
    # ============================================================

    path(
        "customers/",
        views.customer_list_view,
        name="customers",
    ),


    # ============================================================
    # CART
    # ============================================================

    path(
        "cart/",
        views.view_cart,
        name="view_cart",
    ),

    path(
        "updateprice/<int:id>/<int:quantity>/<str:total>/",
        views.update_price,
        name="update_price",
    ),

    path(
        "add-to-cart/<int:Id>/",
        views.add_to_cart,
        name="add_to_cart",
    ),

    path(
        "cart/delete/<int:cart_item_id>/",
        views.delete_cart_item,
        name="delete_cart_item",
    ),


    # ============================================================
    # CHECKOUT & ORDERS
    # ============================================================

    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),

    path(
        "placeorder/",
        views.place_order,
        name="place_order",
    ),

    path(
        "orders/history/",
        views.order_history,
        name="order_history",
    ),


    # ============================================================
    # RAZORPAY
    # ============================================================

    path(
        "razorpay/<int:order_id>/",
        views.create_razorpay_order,
        name="create_razorpay_order",
    ),

    path(
        "payment/success/",
        views.payment_success,
        name="payment_success",
    ),


    # ============================================================
    # EMAIL
    # ============================================================

    path(
        "emailconfirmation/",
        views.send_confirmation_email,
        name="emailconfirmation",
    ),
]


# ================================================================
# MEDIA FILES — DEVELOPMENT ONLY
# ================================================================

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )