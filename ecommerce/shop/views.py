from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Product, Cart
from .forms import SignUpForm
from django.views.decorators.csrf import csrf_exempt
import json
import stripe

# Home page with products
def home(request):
    products = Product.objects.all()
    return render(request, 'shop/home.html', {'products': PRODUCTS})

# Signup functionality
def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect('signup')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'shop/signup.html')

# Login functionality
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials!")
            return redirect('login')

    return render(request, 'shop/login.html')

# Logout functionality
def user_logout(request):
    logout(request)
    return redirect('login')

# Mock PRODUCTS list for testing
PRODUCTS = [
    {"name": "perfume", "price": "10.00", "image": "/shop/images/perfume.jpg", "description": "This is a refreshing fragrance with vibrant citrus notes, offering a burst of zest. The scent settles into a crisp, airy base, leaving a light, breezy finish for an invigorating and fresh experience."},
    {"name": "Perfume2", "price": "15.00", "image": "/shop/images/perfume2.webp", "description": "Eternity perfume with a rich wood scent, blending timeless elegance with earthy notes for a sophisticated and enduring fragrance."},
    {"name": "shoe", "price": "20.00", "image": "/shop/images/shoe.jpeg", "description": "Adidas sports shoes designed for comfort and performance, perfect for athletes and active individuals who demand both style and functionality."},
    {"name": "search shoes", "price": "20.00", "image": "/shop/images/shoe.jpeg", "description": "Comfortable running shoes designed to provide optimal support and flexibility for your workouts, offering both comfort and durability."},
    {"name": "search perfumes", "price": "10.00", "image": "/shop/images/perfume.jpg", "description": "A floral perfume with refreshing citrus top notes, creating a vibrant and light fragrance that’s perfect for everyday wear."},
    {"name": "search watch", "price": "20.00", "image": "/shop/images/watch.png", "description": "Fossil analog watch featuring a classic design and precise craftsmanship, combining style with functionality for any occasion."},
    {"name": "search watch", "price": "10.00", "image": "/shop/images/watch2.jpg", "description": "Branded analog watch with a sleek design, offering a timeless look that pairs well with both formal and casual outfits."},
    {"name": "headphone", "price": "25.0", "image": "/shop/images/headphone.png", "description": "Branded headphones providing high-quality sound and comfort, designed for music lovers and audiophiles who appreciate premium audio performance."},
    {"name": "The Psychology of Marketing", "price": "15.0", "image": "/shop/images/book_harindersingh.jpg", "description": "An insightful audiobook by Harinder Singh Pelia that explores how marketers use psychological strategies to influence consumer behavior. Perfect for visually impaired individuals, this audiobook reveals the hidden tricks of marketing through clear and engaging narration, making it accessible to everyone who wants to understand the art of persuasion and buying habits."},
    {"name": "Talking Clock", "price": "20.0", "image": "/shop/images/talkingclock.jpg", "description": "A convenient and accessible talking clock designed for visually impaired individuals. It announces the time audibly at the press of a button and has an easy-to-use interface with tactile buttons. Ideal for daily use, it also includes alarm and time announcement features for enhanced functionality."}


]

# Search functionality
def search(request):
    query = request.GET.get('query', '')
    results = [product for product in PRODUCTS if query.lower() in product['name'].lower()]
    results_json = json.dumps(results)
    return render(request, 'shop/search_results.html', {
        'query': query,
        'results': results,
        'results_json': results_json,
    })

# Product listing (requires login)
@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

# Add product to cart dynamically
@login_required
def add_to_cart_ajax(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')
        product_image = request.POST.get('product_image')

        # Simulate finding the product from the PRODUCTS list
        product_data = next((p for p in PRODUCTS if p['name'] == product_name), None)
        if product_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'price': product_data['price'],
                    'image': product_data['image'],
                    'description': product_data['description'],
                }
            )
            cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
            if not created:
                cart_item.quantity += 1
            cart_item.save()
            return JsonResponse({'message': 'Product added to cart successfully!'})
        else:
            return JsonResponse({'message': 'Product not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request!'}, status=400)

# View cart (requires login)
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

# Add product to cart from product ID
@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')

# Remove product from cart
@login_required
def remove_from_cart(request, cart_item_id):
    try:
        cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
        cart_item.delete()
        messages.success(request, "Product removed from cart successfully!")
    except Cart.DoesNotExist:
        messages.error(request, "Item not found in cart!")
    return redirect('view_cart')

# Select payment method
@login_required
@csrf_exempt
def select_payment_method(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        payment_method = request.POST.get('payment_method')

        if payment_method not in ['COD', 'Online']:
            return JsonResponse({'message': 'Invalid payment method selected!'}, status=400)

        try:
            cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
            cart_item.payment_method = payment_method
            cart_item.save()
            return JsonResponse({'message': f'Payment method set to {payment_method} successfully!'})
        except Cart.DoesNotExist:
            return JsonResponse({'message': 'Cart item not found!'}, status=404)
    return JsonResponse({'message': 'Invalid request!'}, status=400)

# Process online payment
@login_required
def process_online_payment(request, cart_item_id):
    try:
        cart_item = Cart.objects.get(id=cart_item_id, user=request.user)
        # Simulate payment processing (replace with actual payment gateway integration)
        payment_success = True  # Simulate a successful payment

        if payment_success:
            cart_item.payment_method = 'Online'
            cart_item.save()
            messages.success(request, "Payment successful!")
        else:
            messages.error(request, "Payment failed!")
        return redirect('view_cart')
    except Cart.DoesNotExist:
        messages.error(request, "Cart item not found!")
        return redirect('view_cart')
import stripe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

stripe.api_key = 'sk_test_51Qc1LIFlNATJ2G6NyGajxCNOvYJkb2mEuceLnAdneunl5sxm31NZPP0bJrd3A4a5nTMXCKGvB9W6DPaGbD8CrGHT00Ldox6xij'  # Replace with your Stripe secret key

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item = data['item']
            
            # Create a Stripe Checkout Session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item['name'],
                        },
                        'unit_amount': int(float(item['price']) * 100),  # Convert price to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/success',  # Replace with your success URL
                cancel_url='http://127.0.0.1:8000/cancel',    # Replace with your cancel URL
            )
            return JsonResponse({'id': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
