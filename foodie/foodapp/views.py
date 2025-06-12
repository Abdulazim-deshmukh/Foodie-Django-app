from django.shortcuts import render,get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.hashers import check_password,make_password
import razorpay
from django.conf import settings
from .models import FoodItem
from .models import Customer
from .models import FoodCart
from .models import Orders
from .forms import OrderForm
from .models import Payment
from django.core.mail import send_mail
from django.template.loader import render_to_string



def home(request):
    return render(request,'home.html')


#FoodItem Model

def displayfooditem(request):
    return render(request,'AddFood.html')

def addfooditem(request):
    if request.method=="POST":
        name=request.POST['foodname']
        description=request.POST['fooddescription']
        price=request.POST['foodprice']
        image=request.FILES.get("image")
        data=FoodItem.objects.create(name=name,description=description,price=price,image=image)
        data.save()
    return render(request, "AddFood.html")

def getfooditem(request):
    data=FoodItem.objects.all()
    return render(request,"menu.html",{"menu":data})


def updatefooditem(request, Id):
    food = get_object_or_404(FoodItem, Id=Id)

    if request.method == "POST":
        food.name = request.POST.get('foodname')
        food.description = request.POST.get('fooddescription')
        food.price = request.POST.get('foodprice')

        # Update image if a new one is uploaded
        if 'foodimage' in request.FILES:
            food.image = request.FILES['foodimage']

        food.save()
        return redirect('menu')

    return render(request, 'UpdateFood.html', {'food': food})

def deletefooditem(request, Id):
    food = get_object_or_404(FoodItem, Id=Id)

    if request.method == "POST":
        food.delete()
        return redirect('menu')

    # Confirm delete page
    return render(request, 'DeleteFood.html', {'food': food})

def fooditem_search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = FoodItem.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'searchresult.html', {'results': results, 'query': query})


#customer

def register_customer(request):
    if request.method == "POST":
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Basic validations
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        if Customer.objects.filter(emailId=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "register.html")

        # Hash the password
        hashed_password = make_password(password)

        # Create and save customer with hashed password
        customer = Customer(
            name=name,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            emailId=email,
            password=hashed_password
        )
        customer.save()
        messages.success(request, "Registration successful. Please login.")
        return redirect('login')  # or whatever your login URL name is

    return render(request, "register.html")

def customer_list_view(request):
    customers = Customer.objects.all()
    return render(request, 'customerlist.html', {'customers': customers})






def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Admin login
        if email == 'azim@gmail.com' and password == '1234':
            request.session['admin'] = email
            return redirect('addfood')

        # Customer login
        try:
            customer = Customer.objects.get(emailId=email)
            if check_password(password, customer.password):
                request.session['cust_emailId'] = customer.emailId
                request.session['customer_name'] = customer.name
                return redirect('home')
            else:
                messages.error(request, 'Incorrect password.')
        except Customer.DoesNotExist:
            messages.error(request, 'Customer does not exist.')

    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()  # Clears all session data
    return redirect('logout_success')

def logout_success(request):
    return render(request, 'logoutsuccess.html')


#food cart

def view_cart(request):
    email = request.session.get('cust_emailId')
    if not email:
        return redirect('login')

    customer = get_object_or_404(Customer, emailId=email)
    cart_items = FoodCart.objects.filter(customer=customer)

    total_amount = sum(item.total_price() for item in cart_items)  # call the method here

    return render(request, 'cartlist.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

def update_price(request, id, quantity, total):
    cart_item = get_object_or_404(FoodCart, id=id)
    
    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.save()
    
    return redirect('view_cart')





def add_to_cart(request, Id):
    if 'cust_emailId' not in request.session:
        return redirect('login')

    customer = Customer.objects.get(emailId=request.session['cust_emailId'])
    food = get_object_or_404(FoodItem, Id=Id)

    cart_item, created = FoodCart.objects.get_or_create(customer=customer, food_item=food)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


def delete_cart_item(request, cart_item_id):
    # Optional: check if user is logged in and owns the cart item
    email = request.session.get('cust_emailId')
    if not email:
        return redirect('login')

    customer = get_object_or_404(Customer, emailId=email)
    cart_item = get_object_or_404(FoodCart, id=cart_item_id, customer=customer)
    cart_item.delete()
    return redirect('view_cart')

def checkout(request):
    print("===== CHECKOUT VIEW ACCESSED =====")
    print("Session keys:", request.session.keys())
    print("cust_emailId in session:", request.session.get('cust_emailId'))

    # Get customer email from session
    email = request.session.get('cust_emailId')
    if not email:
        print("Redirecting to login - customer email not in session.")
        return redirect('login')

    customer = get_object_or_404(Customer, emailId=email)
    cart_items = FoodCart.objects.filter(customer=customer)

    if not cart_items.exists():
        print("Cart is empty for:", email)
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    total_amount = sum(item.total_price() for item in cart_items)

    print(f"Customer: {customer.name}, Items in cart: {len(cart_items)}, Total: {total_amount}")

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'customer': customer,
    })




def place_order(request):
    email = request.session.get('cust_emailId')
    if not email:
        return redirect('login')

    customer = get_object_or_404(Customer, emailId=email)
    cart_items = FoodCart.objects.filter(customer=customer)

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('view_cart')

    total_amount = sum(item.total_price() for item in cart_items)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.totalbill = total_amount
            order.save()

            # Create order number after saving
            order.orderNo = f"ORDER{order.id:06d}"
            order.save()


            # Clear cart items from DB
            cart_items.delete()

            # Clear session cart if you use session cart (optional)
            if 'cart' in request.session:
                del request.session['cart']


            messages.success(request, "Order placed successfully!")
            return redirect('create_razorpay_order', order_id=order.id)
        else:
            messages.error(request, "Please fill the form correctly.")
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart_items': cart_items,
        'total_amount': total_amount,
    }
    return render(request, 'checkout.html', context)


def create_razorpay_order(request, order_id):
    try:
        order = get_object_or_404(Orders, pk=order_id)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        razorpay_order = client.order.create({
            "amount": int(order.totalbill * 100),
            "currency": "INR",
            "payment_capture": 1,
        })

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'razorpay_order_id': razorpay_order['id'],
                'amount': order.totalbill,
                'status': 'PENDING',
            }
        )

        context = {
            'order': order,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': payment.razorpay_order_id,
            'amount': int(order.totalbill * 100),
            'name': order.name,
            'email': order.customer.emailId,
            'phone': order.phoneno,
        }
        return render(request, 'paymentpage.html', context)

    except Exception as e:
        print("Error in create_razorpay_order:", e)
        raise


from django.shortcuts import render

def payment_success(request):
    if request.method == "POST":
        razorpay_order_id = request.POST.get("razorpay_order_id")

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.status = "SUCCESS"
            payment.save()

            order = payment.order
            order.is_paid = True
            order.status = "CONFIRMED"
            order.save()

            customer_email = order.customer.emailId

            # Send confirmation email
            send_mail(
                subject="Order Confirmed!",
                message=f"Hi {order.name},\n\nYour order (ID: {order.orderNo}) was placed successfully!\nTotal: ₹{order.totalbill}\n\nThank you for ordering from Foodie!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[customer_email],
                fail_silently=False,
            )

            # Render success template
            return render(request, "paymentsuccess.html", {"order": order})

        except Payment.DoesNotExist:
            return HttpResponse("<h2 style='color:red;'>❌ Payment Not Found</h2>", status=404)

    return HttpResponse("<h2>Invalid request method.</h2>", status=400)



def order_history(request):
    email = request.session.get('cust_emailId')
    if not email:
        return redirect('login')

    customer = get_object_or_404(Customer, emailId=email)
    orders = Orders.objects.filter(customer=customer, is_paid=True).order_by('-created_at')

    return render(request, 'orderhistory.html', {
        'customer': customer,
        'orders': orders,
    })

def send_confirmation_email(request):
    # Get email from session (e.g., stored at login)
    email = request.session.get('cust_emailId')

    if email:
        subject = 'Order Confirmation - Foodie'
        message = 'Thank you for your order. Your food is being prepared!'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
        return render(request, 'emailconfirmation.html')
   

 
