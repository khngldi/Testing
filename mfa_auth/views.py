from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from mfa.models import User_Keys


@login_required
def register_fido_key(request):
    if User_Keys.objects.filter(username=request.user.username).exists():
        return render(request, 'users/register_fido.html')
    return redirect('mfa:register_fido_key')  # Использует встроенную регистрацию django-mfa2
