from django.contrib import admin

from .models import (
    Customer,
    FoodCart,
    FoodItem,
    Orders,
    Payment,
)


# ============================================================
# FOOD ITEM ADMIN
# ============================================================

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "image",
    )

    search_fields = (
        "name",
        "description",
    )

    ordering = (
        "name",
    )


# ============================================================
# CUSTOMER ADMIN
# ============================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "emailId",
        "phone",
        "city",
        "pincode",
    )

    search_fields = (
        "name",
        "emailId",
        "phone",
        "city",
    )

    ordering = (
        "name",
    )


# ============================================================
# FOOD CART ADMIN
# ============================================================

@admin.register(FoodCart)
class FoodCartAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "food_item",
        "quantity",
        "added_at",
    )

    search_fields = (
        "customer__name",
        "customer__emailId",
        "food_item__name",
    )

    list_filter = (
        "added_at",
    )

    readonly_fields = (
        "added_at",
    )

    ordering = (
        "-added_at",
    )


# ============================================================
# ORDER ADMIN
# ============================================================

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = (
        "orderNo",
        "name",
        "customer",
        "totalbill",
        "is_paid",
        "status",
        "created_at",
    )

    search_fields = (
        "orderNo",
        "name",
        "customer__name",
        "customer__emailId",
        "phoneno",
    )

    list_filter = (
        "status",
        "is_paid",
        "created_at",
    )

    readonly_fields = (
        "orderNo",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


# ============================================================
# PAYMENT ADMIN
# ============================================================

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "amount",
        "status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "order__orderNo",
        "order__name",
        "razorpay_order_id",
        "razorpay_payment_id",
    )

    list_filter = (
        "status",
        "payment_method",
        "created_at",
    )

    readonly_fields = (
        "razorpay_order_id",
        "razorpay_payment_id",
        "razorpay_signature",
        "created_at",
    )

    ordering = (
        "-created_at",
    )