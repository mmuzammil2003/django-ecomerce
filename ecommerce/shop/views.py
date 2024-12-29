# from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Product, Cart
from .forms import SignUpForm
#from django.shortcuts import render, redirect
#from django.contrib.auth import authenticate, login
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth.models import User

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

        # Create the user
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'shop/signup.html')



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

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    return render(request, 'shop/home.html')

def user_logout(request):
    logout(request)
    return redirect('login')

PRODUCTS = [
    {"name": "perfume", "price": "$10.00", "image": "/shop/images/perfume.jpg","description": "its a perfume of banana repblic brand .it has citrus notes."},
    {"name": "Perfume2", "price": "$15.00", "image": "/shop/images/perfume2.webp","description": "eternity perfume .it has a wood smell ."},
    {"name": "shoe", "price": "$20.00", "image": "/shop/images/shoe.jpeg","description": "brad nw adidas sports shoes ."},
    {"name": "search shoes", "price": "$20.00", "image": "/shop/images/shoe.jpeg","description": "Comfortable running shoes perfect for everyday use."},
    {"name": " search perfumes", "price": "$10.00", "image": "/shop/images/perfume.jpg","description": "A lovely floral perfume with a touch of citrus."},
    {"name": "search watch", "price": "$20.00", "image": "/shop/images/watch.png","description": "An analog watch of fossil brand "},
    {"name": " search watch", "price": "$10.00", "image": "/shop/images/watch2.jpg","description": "an analog watch its a branded watch."},
    
    
]

import json

def search(request):
    query = request.GET.get('query', '')
    results = [product for product in PRODUCTS if query.lower() in product['name'].lower()]
    results_json = json.dumps(results)  # Convert results to JSON
    return render(request, 'shop/search_results.html', {
        'query': query,
        'results': results,
        'results_json': results_json,  # Pass JSON to template
    })




@login_required(login_url='login')
def home(request):
    # Your home page logic
    return render(request, 'shop/home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'shop/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'shop/login.html', {'error': 'Invalid credentials'})
    return render(request, 'shop/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})

