from django.contrib.auth.models import AbstractUser
from django.db import models


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