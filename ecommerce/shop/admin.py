from django.contrib import admin
from .models import Product, Cart

# Register the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description')  # Display fields in the admin list view
    search_fields = ('name', 'description')         # Add search functionality
    list_filter = ('price',)                        # Add filter by price

# Register the Cart model
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price')  # Fields to display
    search_fields = ('user__username', 'product__name')            # Search by user and product name
    list_filter = ('user',)                                       # Add filter by user
