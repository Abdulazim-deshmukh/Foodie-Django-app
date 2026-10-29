from django.core.validators import MinValueValidator
from django.db import models


# ============================================================
# FOOD ITEM
# ============================================================

class FoodItem(models.Model):
    """
    Represents a food item available in the Foodie menu.
    """

    name = models.CharField(
        max_length=200
    )

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    image = models.ImageField(
        upload_to="food/",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Food Item"
        verbose_name_plural = "Food Items"

    def __str__(self):
        return self.name


# ============================================================
# CUSTOMER
# ============================================================

class Customer(models.Model):
    """
    Customer profile used by the Foodie ordering system.

    The email address remains the primary key for compatibility
    with the existing database and ordering system.

    Django's User model is used separately for authentication.
    """

    name = models.CharField(
        max_length=50
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    pincode = models.CharField(
        max_length=8,
        blank=True,
        null=True
    )

    emailId = models.EmailField(
        primary_key=True,
        max_length=100
    )

    # Kept for compatibility with existing customer records.
    # Authentication is handled by Django's User model.
    password = models.CharField(
        max_length=128
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name


# ============================================================
# FOOD CART
# ============================================================

class FoodCart(models.Model):
    """
    Represents an item currently present in a customer's cart.
    """

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1)
        ]
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-added_at"]
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "customer",
                    "food_item"
                ],
                name="unique_customer_food_item"
            )
        ]

    def __str__(self):
        return (
            f"{self.food_item.name} x {self.quantity} "
            f"- {self.customer.name}"
        )

    def total_price(self):
        """
        Calculate the total price for this cart item.
        """

        return self.quantity * self.food_item.price


# ============================================================
# ORDERS
# ============================================================

class Orders(models.Model):
    """
    Represents a customer's completed checkout/order record.
    """

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    orderNo = models.CharField(
        max_length=100,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    address = models.CharField(
        max_length=255
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=8
    )

    phoneno = models.CharField(
        max_length=15
    )

    totalbill = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[
            MinValueValidator(0)
        ]
    )

    is_paid = models.BooleanField(
        default=False
    )

    ORDER_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.orderNo} by {self.name}"


# ============================================================
# PAYMENT
# ============================================================

class Payment(models.Model):
    """
    Stores Razorpay payment information associated
    with an order.
    """

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    order = models.OneToOneField(
        Orders,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    razorpay_signature = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return (
            f"Payment for Order {self.order.orderNo} "
            f"- {self.status}"
        )