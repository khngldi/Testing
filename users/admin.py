from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'is_seller_approved')
    list_filter = ('role', 'is_active', 'is_seller_approved')
    search_fields = ('username', 'email')
    ordering = ('date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('role', 'profile_picture', 'is_seller_approved'),
        }),
    )
