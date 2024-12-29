from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('search/', views.search, name='search'),  # Search page
]
