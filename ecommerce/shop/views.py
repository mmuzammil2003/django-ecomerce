from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Product, Cart
from .forms import SignUpForm
import json

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
    {"name": "perfume", "price": "$10.00", "image": "/shop/images/perfume.jpg", "description": "This is a refreshing fragrance with vibrant citrus notes, offering a burst of zest. The scent settles into a crisp, airy base, leaving a light, breezy finish for an invigorating and fresh experience."},
    {"name": "Perfume2", "price": "$15.00", "image": "/shop/images/perfume2.webp", "description": "Eternity perfume with a rich wood scent, blending timeless elegance with earthy notes for a sophisticated and enduring fragrance."},
    {"name": "shoe", "price": "$20.00", "image": "/shop/images/shoe.jpeg", "description": "Adidas sports shoes designed for comfort and performance, perfect for athletes and active individuals who demand both style and functionality."},
    {"name": "search shoes", "price": "$20.00", "image": "/shop/images/shoe.jpeg", "description": "Comfortable running shoes designed to provide optimal support and flexibility for your workouts, offering both comfort and durability."},
    {"name": "search perfumes", "price": "$10.00", "image": "/shop/images/perfume.jpg", "description": "A floral perfume with refreshing citrus top notes, creating a vibrant and light fragrance that’s perfect for everyday wear."},
    {"name": "search watch", "price": "$20.00", "image": "/shop/images/watch.png", "description": "Fossil analog watch featuring a classic design and precise craftsmanship, combining style with functionality for any occasion."},
    {"name": "search watch", "price": "$10.00", "image": "/shop/images/watch2.jpg", "description": "Branded analog watch with a sleek design, offering a timeless look that pairs well with both formal and casual outfits."},
    {"name": "headphone", "price": "$25.0", "image": "/shop/images/headphone.png", "description": "Branded headphones providing high-quality sound and comfort, designed for music lovers and audiophiles who appreciate premium audio performance."}
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
