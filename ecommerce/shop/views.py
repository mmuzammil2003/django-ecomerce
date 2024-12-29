from django.shortcuts import render

def home(request):
    return render(request, 'shop/home.html')

PRODUCTS = [
    {"name": "Product 1", "price": "$10.00"},
    {"name": "Product 2", "price": "$15.00"},
    {"name": "Product 3", "price": "$20.00"},
]

def search(request):
    query = request.GET.get('query', '').lower()  # Get the search query
    results = [product for product in PRODUCTS if query in product['name'].lower()]
    return render(request, 'shop/search_results.html', {'query': query, 'results': results})