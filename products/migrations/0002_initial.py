# Generated by Django 5.1.7 on 2025-03-30 12:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='product',
            name='seller',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='like',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product'),
        ),
        migrations.AlterUniqueTogether(
            name='like',
            unique_together={('user', 'product')},
        ),
    ]
