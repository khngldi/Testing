from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    ROLES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
    )

    role = models.CharField(max_length=10, choices=ROLES, default='customer')
    is_seller_approved = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='media/profile_pics/', default='media/profile_pics/default.png')

    def __str__(self):
        return self.username

class PasswordResetRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Запрос на сброс пароля от {self.user.email} ({'использован' if self.is_used else 'активен'})"