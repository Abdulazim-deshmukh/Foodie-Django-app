from django.contrib import admin
from .models import FoodItem
from .models import Customer
from .models import FoodCart
from .models import Orders
from .models import Payment


admin.site.register(FoodItem)
admin.site.register(Customer)
admin.site.register(FoodCart)
admin.site.register(Orders)
admin.site.register(Payment)



# Register your models here.
