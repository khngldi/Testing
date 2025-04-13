from django.urls import path
from . import views

app_name = 'mfa'

urlpatterns = [
    path('register/', views.register_fido_key, name='register_fido_key'),
]