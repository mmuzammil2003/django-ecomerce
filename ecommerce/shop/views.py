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
    {"name": "Vintage Perfume", "price": "10.00", "image": "/shop/images/perfume.jpg", "description": "This is a refreshing fragrance featuring vibrant citrus top notes like lemon and orange, blended with delicate floral hints of jasmine and rose. The scent transitions smoothly into a light, airy base of musk and cedarwood, offering a crisp and breezy finish that creates a refreshing and uplifting experience throughout the day."},

    {"name": "Enternity Perfume", "price": "15.00", "image": "/shop/images/perfume2.webp", "description": "Eternity perfume with a rich and sophisticated scent profile, starting with earthy notes of sandalwood and cedar, complemented by warm hints of amber and musk. Its timeless elegance is further elevated by subtle floral undertones, making it a perfect choice for those who appreciate an enduring and classy fragrance."},
    
    {"name": "Adidas Shoes", "price": "20.00", "image": "/shop/images/shoe.jpeg", "description": "Adidas sports shoes designed with advanced cushioning and breathable mesh fabric for maximum comfort during workouts. The lightweight design ensures agility, while the durable rubber sole provides excellent grip on various surfaces. Ideal for athletes, runners, or anyone leading an active lifestyle."},
    
    {"name": "Puma Shoes", "price": "20.00", "image": "/shop/images/puma shoes.avif", "description": "Comfortable running shoes with a soft insole and a flexible design that adapts to your foot's natural movement. Featuring a stylish and modern look, these shoes provide optimal support for long-distance runs or daily walks, ensuring both durability and performance."},
    
    {"name": "Floral Perfume", "price": "10.00", "image": "/shop/images/Zara perfume.jpg", "description": "A vibrant floral perfume with refreshing citrus top notes of bergamot and grapefruit, balanced by a heart of peony and lily. The fragrance settles into a subtle woody base, making it an ideal choice for casual outings or daily wear, leaving a light and cheerful impression."},
    
    {"name": "Black Watch", "price": "20.00", "image": "/shop/images/watch.png", "description": "A Fossil analog watch featuring a polished stainless steel case and a sophisticated leather strap. The minimalist design is paired with a clear and easy-to-read dial, making it suitable for both formal and casual occasions. Its precise quartz movement ensures reliable timekeeping."},
    
    {"name": "Analog Watch", "price": "10.00", "image": "/shop/images/watch2.jpg", "description": "A branded analog watch with a sleek and modern design, featuring a lightweight yet sturdy metal body. The elegant face includes subtle markers for a timeless aesthetic, perfectly balancing functionality and style for any wardrobe."},
    
    {"name": "Headphone", "price": "25.00", "image": "/shop/images/headphone.png", "description": "Premium branded headphones with high-quality sound performance. The cushioned ear cups provide excellent comfort for extended listening sessions, while the adjustable headband ensures a perfect fit. These headphones deliver deep bass and crystal-clear audio, making them ideal for music enthusiasts, gamers, and professionals alike."},
    
    {"name": "The Psychology of Marketing", "price": "15.0", "image": "/shop/images/book_harindersingh.jpg", "description": "An insightful audiobook by Harinder Singh Pelia that explores how marketers use psychological strategies to influence consumer behavior. Perfect for visually impaired individuals, this audiobook reveals the hidden tricks of marketing through clear and engaging narration, making it accessible to everyone who wants to understand the art of persuasion and buying habits."},
    
    {"name": "Talking Clock", "price": "20.0", "image": "/shop/images/talkingclock.jpg", "description": "A convenient and accessible talking clock designed for visually impaired individuals. It announces the time audibly at the press of a button and has an easy-to-use interface with tactile buttons. Ideal for daily use, it also includes alarm and time announcement features for enhanced functionality."},
    
    {"name": "Toothpaste", "price": "3.00", "image": "/shop/images/paste.jpg", "description": "A refreshing mint-flavored toothpaste, smooth in texture, with a clean, crisp taste that leaves your mouth feeling fresh. It has a slight cooling sensation and is formulated with fluoride to help protect your teeth from cavities and strengthen enamel. Imagine the feeling of brushing your teeth with a minty breeze, leaving your mouth feeling thoroughly cleansed and invigorated."},
    
    {"name": "Soap", "price": "2.50", "image": "/shop/images/soap.jpg", "description": "This moisturizing soap is infused with the gentle, calming scent of aloe vera and coconut oil. As you lather it, you can feel the smoothness of the foam gliding over your skin, leaving it soft and hydrated. The soap is creamy and rich, providing a gentle, soothing touch, with a scent that lingers lightly, making your skin feel refreshed and cared for."},
    
    {"name": "Clothes", "price": "25.00", "image": "/shop/images/clothes1.jpg", "description": "Made of soft, breathable cotton, these clothes offer the perfect balance of comfort and style. The fabric feels light and airy on your skin, allowing you to move freely. Whether you’re wearing a shirt, dress, or pants, the clothes have a relaxed fit, providing ease and flexibility for daily activities. They're designed with simple, yet elegant lines that hug the body comfortably, giving you a sense of both casual ease and stylish confidence."},

    {"name": "Towel", "price": "8.00", "image": "/shop/images/towel.jpg", "description": "This towel is made of thick, plush cotton that absorbs moisture quickly, enveloping you in a warm embrace as it touches your skin. The fabric feels soft, yet substantial, with a slight weight that adds a sense of luxury. Its edges are reinforced, making it durable and long-lasting. After a shower, the towel wraps around you, providing comfort and coziness, while the absorbent texture gently dries your body, leaving you feeling refreshed."},

    {"name": "Nike Shoe", "price": "200.00", "image": "/shop/images/nikeshoe.jpg", "description": "These athletic shoes are perfect for various activities, including running, working out, or casual daily wear. The shoes are lightweight, providing ease of movement, and they feature a cushioned sole that offers excellent support for your feet, reducing fatigue during extended use. The design incorporates three main colors: blue, black, and white, creating a sleek, modern appearance. The upper material is breathable, allowing for airflow to keep your feet cool, while the sole is designed for a firm grip, ensuring safety and stability on different surfaces. Gender: Unisex, crafted for all individuals seeking comfort and performance."},

    {"name": "Mug", "price": "10.50", "image": "/shop/images/Mug.jpg", "description": "This mug is perfect for enjoying your morning coffee or tea. It is made of high-quality ceramic, which feels smooth and solid in your hands. The design on the mug is vibrant and multi-colored, adding a cheerful touch to your day. The mug's color is primarily white, with a multi-colored design that spans its surface. It has a comfortable, sturdy handle that fits snugly in your hand, making it easy to hold and sip from. It is suitable for both hot and cold beverages and is designed to be durable for long-term use. Ideal for anyone who loves a reliable and stylish mug."},
    {"name": "water bottle", "price": "25.00", "image": "/shop/images/waterBottle.jpeg", "description": "This water bottle is your perfect companion for staying hydrated while on the go. It is constructed from durable stainless steel, which gives it a sturdy feel and ensures it remains rust-free over time. The bottle is white in color, sleek, and smooth to the touch, with a slightly tapered design that makes it easy to hold. It features a leak-proof lid with a secure screw-on mechanism, ensuring no accidental spills, even if the bottle is jostled or turned upside down. The lid also has a built-in handle for easy carrying. With its insulated design, it can keep your beverages hot or cold for hours. Suitable for anyone looking for a reliable and stylish hydration solution."},
    {"name": "shampoo bottle", "price": "10.00", "image": "/shop/images/shampoobottle.jpg", "description": " This shampoo bottle is ideal for storing and dispensing your favorite shampoo. The bottle is made of clear plastic, allowing you to easily see how much shampoo is left. Its design features a convenient pump dispenser, which is simple to press and provides a controlled amount of shampoo with each pump, reducing waste. The clear plastic is smooth to the touch, and the pump mechanism is easy to operate, even with wet hands. The bottle's shape is slightly cylindrical, with a stable base that prevents tipping over. Making it a practical choice for anyone looking to organize their bathroom essentials."},

    {"name": "Ceramic Plate", "price": "15.00", "image": "/shop/images/ceramic plate.avif", "description": "The ceramic plate features a smooth, glossy finish that reflects light beautifully, enhancing its aesthetic appeal. It has a classic round shape with a slightly raised edge, providing a sophisticated look. The surface is adorned with subtle, hand-painted floral patterns, adding a touch of artistry. Available in a soft white color with pastel accents, it complements any table setting.This elegant ceramic plate is perfect for serving your favorite dishes. Its smooth, glossy finish adds a touch of sophistication to any table setting. The plate is both microwave and dishwasher safe, making it practical for everyday use. Its durable construction ensures it can withstand regular use while maintaining its beauty. Ideal for both casual meals and special occasions."},
    {"name": "Classic Pen", "price": "5.50", "image": "/shop/images/classicpen.jpeg", "description": "This classic pen has a sleek, elongated body made of polished metal, giving it a premium feel. It features a shiny chrome clip and accents, adding a touch of elegance. The grip is ergonomically designed with a textured surface for comfort during writing. The ink flows smoothly from a fine tip, producing clean, precise lines in deep black or blue ink."},
    {"name": "Cotton Towel", "price": "8.00", "image": "/shop/images/cotton towel.jpg", "description": "The soft cotton towel is plush and fluffy, providing a luxurious feel against the skin. It is generously sized, allowing for easy wrapping after a shower or swim. The towel features a solid color with a subtle ribbed texture along the edges, enhancing its visual appeal. Available in a variety of vibrant colors, it adds a pop of brightness to your bathroom decor."},
    {"name": "Travel Bag", "price": "150.00", "image": "/shop/images/travelbag.jpg", "description": " This spacious travel bag has a rectangular shape with a structured design, providing ample storage space. Made from durable, water-resistant fabric, it features a sleek exterior with minimalistic lines. The bag includes multiple zippered compartments, including a large main section and smaller pockets for organization. It has sturdy, padded handles and an adjustable shoulder strap, both designed for comfort and ease of carrying. Available in a stylish black or navy blue, it is perfect for both casual and business travel."},



    {"name": "Towel", "price": "8.00", "image": "/shop/images/towel.jpg", "description": "This towel is made of thick, plush cotton that absorbs moisture quickly, enveloping you in a warm embrace as it touches your skin. The fabric feels soft, yet substantial, with a slight weight that adds a sense of luxury. Its edges are reinforced, making it durable and long-lasting. After a shower, the towel wraps around you, providing comfort and coziness, while the absorbent texture gently dries your body, leaving you feeling refreshed."},


    
    {"name": "Mug", "price": "10.50", "image": "/shop/images/Mug.jpg", "description": "This mug is perfect for enjoying your morning coffee or tea. It is made of high-quality ceramic, which feels smooth and solid in your hands. The design on the mug is vibrant and multi-colored, adding a cheerful touch to your day. The mug's color is primarily white, with a multi-colored design that spans its surface. It has a comfortable, sturdy handle that fits snugly in your hand, making it easy to hold and sip from. It is suitable for both hot and cold beverages and is designed to be durable for long-term use. Ideal for anyone who loves a reliable and stylish mug."},
    
    {"name": "water bottle", "price": "25.00", "image": "/shop/images/waterBottle.jpeg", "description": "This water bottle is your perfect companion for staying hydrated while on the go. It is constructed from durable stainless steel, which gives it a sturdy feel and ensures it remains rust-free over time. The bottle is white in color, sleek, and smooth to the touch, with a slightly tapered design that makes it easy to hold. It features a leak-proof lid with a secure screw-on mechanism, ensuring no accidental spills, even if the bottle is jostled or turned upside down. The lid also has a built-in handle for easy carrying. With its insulated design, it can keep your beverages hot or cold for hours. Suitable for anyone looking for a reliable and stylish hydration solution."},
    
    {"name": "shampoo bottle", "price": "10.00", "image": "/shop/images/shampoobottle.jpg", "description": " This shampoo bottle is ideal for storing and dispensing your favorite shampoo. The bottle is made of clear plastic, allowing you to easily see how much shampoo is left. Its design features a convenient pump dispenser, which is simple to press and provides a controlled amount of shampoo with each pump, reducing waste. The clear plastic is smooth to the touch, and the pump mechanism is easy to operate, even with wet hands. The bottle's shape is slightly cylindrical, with a stable base that prevents tipping over. Making it a practical choice for anyone looking to organize their bathroom essentials."},

    {"name": "Ceramic Plate", "price": "15.00", "image": "/shop/images/ceramic plate.avif", "description": "The ceramic plate features a smooth, glossy finish that reflects light beautifully, enhancing its aesthetic appeal. It has a classic round shape with a slightly raised edge, providing a sophisticated look. The surface is adorned with subtle, hand-painted floral patterns, adding a touch of artistry. Available in a soft white color with pastel accents, it complements any table setting.This elegant ceramic plate is perfect for serving your favorite dishes. Its smooth, glossy finish adds a touch of sophistication to any table setting. The plate is both microwave and dishwasher safe, making it practical for everyday use. Its durable construction ensures it can withstand regular use while maintaining its beauty. Ideal for both casual meals and special occasions."},
    
    {"name": "Classic Pen", "price": "5.50", "image": "/shop/images/classicpen.jpeg", "description": "This classic pen has a sleek, elongated body made of polished metal, giving it a premium feel. It features a shiny chrome clip and accents, adding a touch of elegance. The grip is ergonomically designed with a textured surface for comfort during writing. The ink flows smoothly from a fine tip, producing clean, precise lines in deep black or blue ink."},
    
    {"name": "Cotton Towel", "price": "8.00", "image": "/shop/images/cotton towel.jpg", "description": "The soft cotton towel is plush and fluffy, providing a luxurious feel against the skin. It is generously sized, allowing for easy wrapping after a shower or swim. The towel features a solid color with a subtle ribbed texture along the edges, enhancing its visual appeal. Available in a variety of vibrant colors, it adds a pop of brightness to your bathroom decor."},
    
    {"name": "Travel Bag", "price": "150.00", "image": "/shop/images/travelbag.jpg", "description": " This spacious travel bag has a rectangular shape with a structured design, providing ample storage space. Made from durable, water-resistant fabric, it features a sleek exterior with minimalistic lines. The bag includes multiple zippered compartments, including a large main section and smaller pockets for organization. It has sturdy, padded handles and an adjustable shoulder strap, both designed for comfort and ease of carrying. Available in a stylish black or navy blue, it is perfect for both casual and business travel."},

    {"name": "Black tshirt", "price": "20.00", "image": "/shop/images/blackshirt.jpeg", "description": "This oversized black t-shirt is designed for unisex wear, featuring a crew neckline and short sleeves. Made from soft and comfortable fabric, it offers a minimalist look that pairs effortlessly with any outfit, making it a versatile choice for daily use."},
    
    {"name": "White dress", "price": "25.50", "image": "/shop/images/cotton dress.jpg", "description": "A breezy, flowy white dress tailored for women, boasting a v-neckline and a slightly asymmetrical hem. With its lightweight and breathable material, the dress offers side pockets and a relaxed fit, making it ideal for warm weather and adaptable for both casual and semi-formal occasions."},
    
    {"name": "black sunglasses", "price": "10.00", "image": "/shop/images/smartglasses.webp", "description": "Sporty black sunglasses crafted for unisex use, featuring a wide frame and a durable, comfortable fit. These sunglasses provide essential UV protection and a sleek, modern aesthetic, perfect for daily wear and outdoor activities."},
    
    {"name": "smart speaker", "price": "50.00", "image": "/shop/images/speaker.jpeg", "description": " A sophisticated black smart speaker with a cylindrical design and an integrated display, offering a premium and minimalist appearance. This high-quality device delivers exceptional audio performance, voice control functionality, and the ability to manage smart home devices, stream music, and handle calls."},
    
    {"name": "white tshirt", "price": "23.00", "image": "/shop/images/travelbag.jpg", "description": " This white t-shirt for men features a bold graphic design of a yellow smiley face and the words Talking Heads on the front. Made from soft, comfortable fabric, it’s a playful and stylish nod to the iconic band, perfect for casual everyday wear."},

    {"name": "Music Player", "price": "150.00", "image": "/shop/images/music_player.jpg", "description": "A sleek and portable music device designed for audiophiles and casual listeners alike. The music player features a lightweight, compact design with a smooth matte finish that feels comfortable in your hand. It has an intuitive interface with a vibrant touchscreen display that is easy to navigate, even for visually impaired users, thanks to voice-guided menus and tactile button edges. Equipped with high-resolution audio output, it delivers crystal-clear sound with deep bass, rich mids, and crisp highs, making every note come alive. The device supports multiple audio formats and offers expandable storage to carry your entire music library. With up to 30 hours of battery life, you can enjoy uninterrupted music on long trips. The built-in Bluetooth connectivity lets you pair it with wireless headphones or speakers, and the 3.5mm jack ensures compatibility with traditional wired options. Imagine the joy of slipping into a world of immersive sound, whether you're relaxing at home or on the go, with this versatile and stylish music companion."},
    
    {"name": "Smartwatch", "price": "200.00", "image": "/shop/images/smartwatch.jpg", "description": "A stylish and modern smartwatch designed for fitness enthusiasts and tech-savvy individuals. The watch features a sleek, round display with customizable watch faces and a durable, lightweight strap that is comfortable for all-day wear. It comes equipped with advanced health-tracking features, including heart rate monitoring, sleep analysis, and blood oxygen level measurement. The built-in GPS allows you to track your runs or hikes with precision, while the fitness modes cater to various activities like yoga, swimming, and cycling. With its waterproof design, you can wear it during intense workouts or even while swimming. Notifications for calls, texts, and apps keep you connected on the go, and voice assistant integration adds convenience to your daily tasks. The battery lasts up to 7 days on a single charge, ensuring reliable performance throughout your week. Imagine the ease of managing your fitness goals, staying connected, and adding a touch of elegance to your wrist with this all-in-one wearable device."},
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
