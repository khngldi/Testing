from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('<int:pk>/like/', views.toggle_like, name='toggle_like'),
    path('<int:pk>/edit/', views.edit_product, name='edit_product'),
    path('<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('add/', views.add_product, name='add_product'),
]