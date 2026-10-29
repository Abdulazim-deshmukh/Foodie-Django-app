"""
Views for the Foodie application.
"""

from decimal import Decimal

import razorpay

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OrderForm, RegistrationForm
from .models import Customer, FoodCart, FoodItem, Orders, Payment


# ============================================================
# HOME
# ============================================================

def home(request):
    """
    Display the Foodie home page.
    """

    return render(
        request,
        "home.html"
    )


# ============================================================
# FOOD MANAGEMENT
# ============================================================

@login_required
def displayfooditem(request):
    """
    Display the add-food page.

    Only staff users can access food management.
    """

    if not request.user.is_staff:
        messages.error(
            request,
            "You do not have permission to manage food."
        )
        return redirect("home")

    return render(
        request,
        "AddFood.html"
    )


@login_required
def addfooditem(request):
    """
    Add a new food item.

    Only staff users can add food items.
    """

    if not request.user.is_staff:
        messages.error(
            request,
            "You do not have permission to add food."
        )
        return redirect("home")

    if request.method == "POST":

        name = request.POST.get(
            "foodname",
            ""
        ).strip()

        description = request.POST.get(
            "fooddescription",
            ""
        ).strip()

        price = request.POST.get(
            "foodprice",
            ""
        ).strip()

        image = request.FILES.get("image")

        if not name or not description or not price:
            messages.error(
                request,
                "Please fill in all required fields."
            )

            return render(
                request,
                "AddFood.html"
            )

        try:
            price = Decimal(price)

            if price < 0:
                raise ValueError

        except (ValueError, TypeError, ArithmeticError):

            messages.error(
                request,
                "Please enter a valid price."
            )

            return render(
                request,
                "AddFood.html"
            )

        FoodItem.objects.create(
            name=name,
            description=description,
            price=price,
            image=image
        )

        messages.success(
            request,
            "Food item added successfully."
        )

        return redirect("menu")

    return render(
        request,
        "AddFood.html"
    )


def getfooditem(request):
    """
    Display all food items.
    """

    data = FoodItem.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "menu.html",
        {
            "menu": data
        }
    )


@login_required
def updatefooditem(request, Id):
    """
    Update an existing food item.

    Only staff users can update food items.
    """

    if not request.user.is_staff:
        messages.error(
            request,
            "You do not have permission to update food."
        )

        return redirect("home")

    # IMPORTANT:
    # FoodItem uses Django's default primary key: id
    food = get_object_or_404(
        FoodItem,
        id=Id
    )

    if request.method == "POST":

        name = request.POST.get(
            "foodname",
            ""
        ).strip()

        description = request.POST.get(
            "fooddescription",
            ""
        ).strip()

        price = request.POST.get(
            "foodprice",
            ""
        ).strip()

        if not name or not description or not price:

            messages.error(
                request,
                "Please fill in all required fields."
            )

            return render(
                request,
                "UpdateFood.html",
                {
                    "food": food
                }
            )

        try:
            price = Decimal(price)

            if price < 0:
                raise ValueError

        except (ValueError, TypeError, ArithmeticError):

            messages.error(
                request,
                "Please enter a valid price."
            )

            return render(
                request,
                "UpdateFood.html",
                {
                    "food": food
                }
            )

        food.name = name
        food.description = description
        food.price = price

        if "foodimage" in request.FILES:
            food.image = request.FILES[
                "foodimage"
            ]

        food.save()

        messages.success(
            request,
            "Food item updated successfully."
        )

        return redirect("menu")

    return render(
        request,
        "UpdateFood.html",
        {
            "food": food
        }
    )


@login_required
def deletefooditem(request, Id):
    """
    Delete a food item.

    Only staff users can delete food items.
    """

    if not request.user.is_staff:
        messages.error(
            request,
            "You do not have permission to delete food."
        )

        return redirect("home")

    # IMPORTANT:
    # FoodItem uses Django's default primary key: id
    food = get_object_or_404(
        FoodItem,
        id=Id
    )

    if request.method == "POST":

        food.delete()

        messages.success(
            request,
            "Food item deleted successfully."
        )

        return redirect("menu")

    return render(
        request,
        "DeleteFood.html",
        {
            "food": food
        }
    )


def fooditem_search(request):
    """
    Search food items by name or description.
    """

    query = request.GET.get(
        "q",
        ""
    ).strip()

    results = FoodItem.objects.none()

    if query:

        results = FoodItem.objects.filter(
            Q(name__icontains=query)
            |
            Q(description__icontains=query)
        ).order_by(
            "name"
        )

    return render(
        request,
        "searchresult.html",
        {
            "results": results,
            "query": query
        }
    )


# ============================================================
# AUTHENTICATION
# ============================================================

def register_customer(request):
    """
    Register a new customer using Django's User system.
    """

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = RegistrationForm(
            request.POST
        )

        if form.is_valid():

            name = form.cleaned_data[
                "name"
            ]

            email = form.cleaned_data[
                "email"
            ].lower()

            password = form.cleaned_data[
                "password"
            ]

            # Create Django authentication user.
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            # Create the application's customer profile.
            Customer.objects.create(
                name=name,
                emailId=email,
                password=""
            )

            login(
                request,
                user
            )

            messages.success(
                request,
                "Account created successfully."
            )

            return redirect("home")

    else:

        form = RegistrationForm()

    return render(
        request,
        "register.html",
        {
            "form": form
        }
    )


def login_view(request):
    """
    Log a customer into the Foodie application.

    Authentication is handled through Django's User system.
    A legacy Customer-session fallback is retained so that
    existing customer records remain usable.
    """

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        email = request.POST.get(
            "email",
            ""
        ).strip().lower()

        password = request.POST.get(
            "password",
            ""
        )

        # ----------------------------------------------------
        # Django authentication
        # ----------------------------------------------------

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            # Keep the legacy customer session available
            # for the existing cart/order system.
            try:

                customer = Customer.objects.get(
                    emailId=email
                )

                request.session[
                    "cust_emailId"
                ] = customer.emailId

                request.session[
                    "customer_name"
                ] = customer.name

            except Customer.DoesNotExist:

                pass

            messages.success(
                request,
                "Welcome back!"
            )

            return redirect("home")

        # ----------------------------------------------------
        # Legacy Customer authentication fallback
        # ----------------------------------------------------

        try:

            customer = Customer.objects.get(
                emailId=email
            )

            from django.contrib.auth.hashers import check_password

            if customer.password and check_password(
                password,
                customer.password
            ):

                # Find the corresponding Django user.
                # If this is an older customer account and the
                # Django User does not exist yet, create it now.
                legacy_user, created = User.objects.get_or_create(
                    username=email,
                    defaults={
                        "email": email,
                        "first_name": customer.name
                    }
                )

                # Sync the password from the verified legacy
                # Customer record into Django authentication.
                legacy_user.set_password(password)
                legacy_user.save()

                # Log the customer into Django authentication.
                login(
                    request,
                    legacy_user
                )

                request.session[
                    "cust_emailId"
                ] = customer.emailId

                request.session[
                    "customer_name"
                ] = customer.name

                messages.success(
                    request,
                    "Welcome back!"
                )

                return redirect("home")

            messages.error(
                request,
                "Incorrect email or password."
            )

        except Customer.DoesNotExist:

            messages.error(
                request,
                "Incorrect email or password."
            )

    return render(
        request,
        "login.html"
    )
@login_required
def logout_view(request):
    """
    Log the current user out and clear the legacy session.
    """

    logout(request)

    request.session.flush()

    return redirect(
        "logout_success"
    )


def logout_success(request):
    """
    Display the logout confirmation page.
    """

    return render(
        request,
        "logoutsuccess.html"
    )


# ============================================================
# CUSTOMER MANAGEMENT
# ============================================================

@login_required
def customer_list_view(request):
    """
    Display all customers.

    Only staff users can access the customer list.
    """

    if not request.user.is_staff:
        messages.error(
            request,
            "You do not have permission to view customers."
        )

        return redirect("home")

    customers = Customer.objects.all().order_by(
        "name"
    )

    return render(
        request,
        "customerlist.html",
        {
            "customers": customers
        }
    )


# ============================================================
# CUSTOMER HELPER
# ============================================================

def get_current_customer(request):
    """
    Return the Customer record associated with the
    currently authenticated user.
    """

    if not request.user.is_authenticated:
        return None

    email = (
        request.user.email
        or request.user.username
    )

    if not email:
        return None

    return Customer.objects.filter(
        emailId__iexact=email
    ).first()


# ============================================================
# FOOD CART
# ============================================================

@login_required
def view_cart(request):
    """
    Display the current customer's cart.
    """

    customer = get_current_customer(
        request
    )

    if customer is None:

        messages.error(
            request,
            "Customer profile not found."
        )

        return redirect("home")

    cart_items = (
        FoodCart.objects
        .filter(customer=customer)
        .select_related("food_item")
    )

    total_amount = sum(
        item.total_price()
        for item in cart_items
    )

    return render(
        request,
        "cartlist.html",
        {
            "cart_items": cart_items,
            "total_amount": total_amount
        }
    )


@login_required
def update_price(
    request,
    id,
    quantity,
    total
):
    """
    Update the quantity of a cart item.

    The cart item must belong to the current customer.
    """

    customer = get_current_customer(
        request
    )

    if customer is None:
        return redirect("login")

    cart_item = get_object_or_404(
        FoodCart,
        id=id,
        customer=customer
    )

    if quantity <= 0:

        cart_item.delete()

    else:

        cart_item.quantity = quantity

        cart_item.save(
            update_fields=[
                "quantity"
            ]
        )

    return redirect(
        "view_cart"
    )


@login_required
def add_to_cart(request, Id):
    """
    Add a food item to the current customer's cart.

    If the food item is already in the cart,
    increase its quantity by one.
    """

    customer = get_current_customer(
        request
    )

    if customer is None:

        messages.error(
            request,
            "Please log in to add items to your cart."
        )

        return redirect("login")

    # IMPORTANT:
    # FoodItem uses Django's default primary key: id
    food = get_object_or_404(
        FoodItem,
        id=Id
    )

    cart_item, created = FoodCart.objects.get_or_create(
        customer=customer,
        food_item=food
    )

    if not created:

        cart_item.quantity += 1

        cart_item.save(
            update_fields=[
                "quantity"
            ]
        )

    messages.success(
        request,
        f"{food.name} added to your cart."
    )

    return redirect(
        "view_cart"
    )


@login_required
def delete_cart_item(
    request,
    cart_item_id
):
    """
    Remove an item from the current customer's cart.
    """

    customer = get_current_customer(
        request
    )

    if customer is None:
        return redirect("login")

    cart_item = get_object_or_404(
        FoodCart,
        id=cart_item_id,
        customer=customer
    )

    cart_item.delete()

    messages.success(
        request,
        "Item removed from your cart."
    )

    return redirect(
        "view_cart"
    )


# ============================================================
# CHECKOUT
# ============================================================

@login_required
def checkout(request):
    """
    Display the checkout page.
    """

    customer = get_current_customer(
        request
    )

    if customer is None:

        messages.error(
            request,
            "Customer profile not found."
        )

        return redirect("home")

    cart_items = (
        FoodCart.objects
        .filter(customer=customer)
        .select_related("food_item")
    )

    if not cart_items.exists():

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect(
            "menu"
        )

    total_amount = sum(
        item.total_price()
        for item in cart_items
    )

    form = OrderForm(
        initial={
            "name": customer.name,
            "address": customer.address or "",
            "city": customer.city or "",
            "pincode": customer.pincode or "",
        }
    )

    return render(
        request,
        "checkout.html",
        {
            "form": form,
            "cart_items": cart_items,
            "total_amount": total_amount,
            "customer": customer,
        }
    )


# ============================================================
# PLACE ORDER
# ============================================================

@login_required
def place_order(request):
    """
    Create an order from the current customer's cart.
    """

    if request.method != "POST":
        return redirect("checkout")

    customer = get_current_customer(
        request
    )

    if customer is None:

        messages.error(
            request,
            "Customer profile not found."
        )

        return redirect("home")

    cart_items = (
        FoodCart.objects
        .filter(customer=customer)
        .select_related("food_item")
    )

    if not cart_items.exists():

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect(
            "menu"
        )

    form = OrderForm(
        request.POST
    )

    if not form.is_valid():

        total_amount = sum(
            item.total_price()
            for item in cart_items
        )

        return render(
            request,
            "checkout.html",
            {
                "form": form,
                "cart_items": cart_items,
                "total_amount": total_amount,
                "customer": customer,
            }
        )

    total_amount = sum(
        item.total_price()
        for item in cart_items
    )

    order = form.save(
        commit=False
    )

    order.customer = customer
    order.totalbill = total_amount
    order.is_paid = False
    order.status = "PENDING"

    # Temporary unique order number.
    order.orderNo = (
        f"ORDER{customer.orders.count() + 1:06d}"
    )

    # Make sure the order number remains unique.
    while Orders.objects.filter(
        orderNo=order.orderNo
    ).exists():

        order.orderNo = (
            f"ORDER{Orders.objects.count() + 1:06d}"
        )

    order.save()

    # Remove purchased items from the cart.
    cart_items.delete()

    messages.success(
        request,
        "Your order has been created."
    )

    return redirect(
        "create_razorpay_order",
        order_id=order.id
    )


# ============================================================
# RAZORPAY
# ============================================================

@login_required
def create_razorpay_order(
    request,
    order_id
):
    """
    Create a Razorpay order for the selected Foodie order.
    """

    customer = get_current_customer(
        request
    )

    if customer is None:
        return redirect("login")

    order = get_object_or_404(
        Orders,
        id=order_id,
        customer=customer
    )

    amount = int(
        order.totalbill * 100
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    razorpay_order = client.order.create(
        {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1,
        }
    )

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "razorpay_order_id":
                razorpay_order["id"],
            "amount":
                order.totalbill,
            "status":
                "PENDING",
        }
    )

    if not created:

        payment.razorpay_order_id = (
            razorpay_order["id"]
        )

        payment.amount = (
            order.totalbill
        )

        payment.status = "PENDING"

        payment.save()

    return render(
        request,
        "paymentpage.html",
        {
            "order": order,
            "razorpay_key":
                settings.RAZORPAY_KEY_ID,
            "razorpay_order_id":
                razorpay_order["id"],
            "amount":
                amount,
            "name":
                order.name,
            "email":
                customer.emailId,
            "phone":
                order.phoneno,
        }
    )


# ============================================================
# PAYMENT SUCCESS
# ============================================================

@login_required
def payment_success(request):
    """
    Verify a successful Razorpay payment and update
    the associated Foodie order.
    """

    if request.method != "POST":
        return redirect("menu")

    razorpay_payment_id = request.POST.get(
        "razorpay_payment_id"
    )

    razorpay_order_id = request.POST.get(
        "razorpay_order_id"
    )

    razorpay_signature = request.POST.get(
        "razorpay_signature"
    )

    if not all(
        [
            razorpay_payment_id,
            razorpay_order_id,
            razorpay_signature,
        ]
    ):

        messages.error(
            request,
            "Payment verification information is incomplete."
        )

        return redirect(
            "order_history"
        )

    customer = get_current_customer(
        request
    )

    if customer is None:
        return redirect("login")

    payment = get_object_or_404(
        Payment.objects.select_related(
            "order"
        ),
        razorpay_order_id=razorpay_order_id,
        order__customer=customer
    )

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    try:

        client.utility.verify_payment_signature(
            {
                "razorpay_order_id":
                    razorpay_order_id,
                "razorpay_payment_id":
                    razorpay_payment_id,
                "razorpay_signature":
                    razorpay_signature,
            }
        )

    except razorpay.errors.SignatureVerificationError:

        payment.status = "FAILED"

        payment.save(
            update_fields=[
                "status"
            ]
        )

        messages.error(
            request,
            "Payment verification failed."
        )

        return redirect(
            "order_history"
        )

    payment.razorpay_payment_id = (
        razorpay_payment_id
    )

    payment.razorpay_signature = (
        razorpay_signature
    )

    payment.status = "SUCCESS"

    payment.save()

    order = payment.order

    order.is_paid = True
    order.status = "CONFIRMED"

    order.save(
        update_fields=[
            "is_paid",
            "status",
            "updated_at",
        ]
    )

    # Send confirmation email.
    try:

        send_mail(
            subject=f"Foodie Order Confirmation - {order.orderNo}",
            message=(
                f"Thank you for your order.\n\n"
                f"Order Number: {order.orderNo}\n"
                f"Total Amount: ₹{order.totalbill}\n"
                f"Payment Status: Successful\n"
                f"Order Status: {order.status}\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[
                customer.emailId
            ],
            fail_silently=True,
        )

    except Exception:
        pass

    return render(
        request,
        "paymentsuccess.html",
        {
            "order": order
        }
    )


# ============================================================
# ORDER HISTORY
# ============================================================

@login_required
def order_history(request):
    """
    Display paid orders belonging to the current customer.
    """

    customer = get_current_customer(
        request
    )

    if customer is None:

        messages.error(
            request,
            "Customer profile not found."
        )

        return redirect("home")

    orders = Orders.objects.filter(
        customer=customer,
        is_paid=True
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "orderhistory.html",
        {
            "orders": orders
        }
    )


# ============================================================
# EMAIL CONFIRMATION
# ============================================================

@login_required
def send_confirmation_email(request):
    """
    Send a simple confirmation email for an order.
    """

    customer = get_current_customer(
        request
    )

    if customer is None:
        return redirect("login")

    order_id = request.GET.get(
        "order_id"
    )

    if not order_id:
        messages.error(
            request,
            "Order information is missing."
        )

        return redirect(
            "order_history"
        )

    order = get_object_or_404(
        Orders,
        id=order_id,
        customer=customer
    )

    send_mail(
        subject=f"Foodie Order Confirmation - {order.orderNo}",
        message=(
            f"Thank you for ordering from Foodie.\n\n"
            f"Order Number: {order.orderNo}\n"
            f"Order Status: {order.status}\n"
            f"Total Amount: ₹{order.totalbill}\n"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[
            customer.emailId
        ],
        fail_silently=True,
    )

    messages.success(
        request,
        "Confirmation email sent successfully."
    )

    return redirect(
        "order_history"
    )