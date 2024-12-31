# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),  # Home page
#     path('search/', views.search, name='search'),  # Search page
# ]


from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup, name='signup'),  # Default root redirects to signup
    path('signup/', views.signup, name='signup'),  # Signup page
    path('login/', views.user_login, name='login'),  # Login page
    path('home/', views.home, name='home'),  # Home page
    path('logout/', views.user_logout, name='logout'),  # Logout page
    path('search/', views.search, name='search'),  # Search page
    path('products/', views.product_list, name='product_list'),  # Product list
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),  # Add to cart
    path('cart/', views.view_cart, name='view_cart'),  # Cart page
    path('create-checkout-session', views.create_checkout_session, name='create-checkout-session'),
]

