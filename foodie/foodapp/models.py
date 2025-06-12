from django.db import models
from django.utils import timezone

# Create your models here.
class FoodItem(models.Model):
    Id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField(default=0.0,null=False)
    image = models.ImageField(upload_to='media/', blank=True, null=True)
    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=8, blank=True, null=True)
    emailId = models.CharField(primary_key=True, max_length=100)
    password = models.CharField(max_length=128)
    def __str__(self):
        return self.name

class FoodCart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_item.name} x {self.quantity} - {self.customer.name}"

    def total_price(self):
        return self.quantity * self.food_item.price
    

class Orders(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    orderNo = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.BigIntegerField()
    phoneno = models.BigIntegerField()
    totalbill = models.FloatField(default=0.0)

    is_paid = models.BooleanField(default=False)
    
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.orderNo} by {self.name}"


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    order = models.OneToOneField(Orders, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.FloatField()
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=50, blank=True, null=True)  # e.g., 'card', 'upi'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.orderNo} - {self.status}"







