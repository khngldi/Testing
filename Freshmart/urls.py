from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views as user_views
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('change-password/', user_views.change_password, name='change_password'),
    path('logout/', user_views.custom_logout, name='logout'),
    path('products/', include('products.urls')),
    path('', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
    path('', include('chatbot.urls')),
    path('mfa/', include('mfa_auth.urls', namespace='mfa_auth')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_URL)