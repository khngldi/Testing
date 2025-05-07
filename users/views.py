import random
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    CustomUserCreationForm,
    CustomUserChangeForm,
    ProfilePictureForm,
    CustomPasswordChangeForm
)
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import CustomUser
from mfa.FIDO2 import begin_registeration, complete_reg, getServer, getUserCredentials
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from fido2.utils import websafe_encode
from django.utils.crypto import get_random_string
from .models import PasswordResetRequest

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)

            if user.role == 'seller':
                user.is_active = False  #временно отключить вход
                user.save()

                #Ссылки
                approve_url = f"http://127.0.0.1:8000/users/approve/{user.id}/"
                reject_url = f"http://127.0.0.1:8000/users/reject/{user.id}/"

                html_message = f"""
                <h2>Новый продавец ожидает подтверждения</h2>
                <p>Пользователь {user.username} хочет стать продавцом.</p>
                <p>
                    <a href="{approve_url}" style="padding:10px 15px;background:#4CAF50;color:white;text-decoration:none;border-radius:5px;">Принять</a>
                    &nbsp;
                    <a href="{reject_url}" style="padding:10px 15px;background:#f44336;color:white;text-decoration:none;border-radius:5px;">Отклонить</a>
                </p>
                """

                send_mail(
                    subject='Новый запрос на регистрацию продавца',
                    message='Ваш почтовый клиент не поддерживает HTML.',
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['khanekshakh@gmail.com'],
                )

                messages.info(request, 'Ваш запрос отправлен. Ожидайте подтверждение продавца.')
                return redirect('home')
            else:
                user.save()
                login(request, user)
                messages.success(request, 'Registration successful!')
                return redirect('products:product_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        profile_form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = ProfilePictureForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('home')

def approve_seller(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()
    return HttpResponse(f'Пользователь {user.username} одобрен как продавец.')

def reject_seller(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return HttpResponse(f'Пользователь {user.username} был отклонён и удалён.')

def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.filter(email=email).first()

        if user:
            confirm_url = f"http://127.0.0.1:8000/users/admin-confirm-reset/{user.id}/"
            html_message = render_to_string('users/reset_request_email.html', {
                'user': user,
                'confirm_url': confirm_url,
            })

            send_mail(
                subject='Запрос на сброс пароля',
                message='Ваш почтовый клиент не поддерживает HTML.',
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['khanekshakh@gmail.com'],  # email админа
            )
            messages.success(request, 'Запрос на сброс пароля отправлен администратору.')
        else:
            messages.error(request, 'Пользователь с таким email не найден.')
        return redirect('login')

    return render(request, 'users/password_reset_form.html')


def admin_confirm_reset(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    new_password = str(random.randint(100000, 999999))  # 6-значный

    user.set_password(new_password)
    user.save()

    send_mail(
        subject='Ваш новый пароль',
        message=f'Ваш пароль был сброшен администратором. Новый пароль: {new_password}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

    return HttpResponse(f'Пароль для {user.email} успешно сброшен и отправлен.')

def approve_reset_request(request, reset_id):
    reset_request = get_object_or_404(PasswordResetRequest, id=reset_id, is_used=False)
    user = reset_request.user

    new_password = get_random_string(length=6, allowed_chars='0123456789')

    user.set_password(new_password)
    user.save()

    reset_request.is_used = True
    reset_request.save()

    send_mail(
        subject='Сброс пароля на Freshmart',
        message=f'Здравствуйте, {user.username}!\n\nВаш новый пароль: {new_password}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return HttpResponse("Пароль успешно сброшен и отправлен пользователю на почту.")

#MFA
def register_fido_key(request):
    return render(request, 'users/register_fido.html')

@login_required
def start_fido(request):
    return begin_registeration(request)


@login_required
@csrf_exempt
def complete_fido(request):
    return complete_reg(request)

def begin_registeration(request):
    server = getServer()
    user_info = {
        u'id': request.user.username.encode("utf8"),
        u'name': f"{request.user.first_name} {request.user.last_name}",
        u'displayName': request.user.username,
    }
    credentials = getUserCredentials(request.user.username)

    registration_data, state = server.register_begin(user_info, credentials)
    request.session['fido_state'] = state

    public_key_data = registration_data.get("publicKey")
    if not public_key_data or "challenge" not in public_key_data:
        return JsonResponse({"error": "Challenge not found in publicKey"}, status=500)

    public_key_data["challenge"] = websafe_encode(public_key_data["challenge"])
    public_key_data["user"]["id"] = websafe_encode(public_key_data["user"]["id"])
    for cred in public_key_data.get("excludeCredentials", []):
        cred["id"] = websafe_encode(cred["id"])

    return JsonResponse({"publicKey": public_key_data})
