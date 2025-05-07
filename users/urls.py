from django.urls import path
from . import views

urlpatterns = [
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('admin-confirm-reset/<int:user_id>/', views.admin_confirm_reset, name='admin_confirm_reset'),
    path('register-fido/', views.register_fido_key, name='register_fido_key'),
    path('approve/<int:user_id>/', views.approve_seller, name='approve_seller'),
    path('reject/<int:user_id>/', views.reject_seller, name='reject_seller'),
    path('register/fido/start/', views.start_fido, name='start_fido'),  # начать регистрацию
    path('register/fido/complete/', views.complete_fido, name='complete_fido'),  # завершить
]
