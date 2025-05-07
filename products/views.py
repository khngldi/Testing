from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Like
from .forms import ProductForm

def home(request):
    popular_products = Product.objects.annotate(
        like_count=Count('like')
    ).order_by('-like_count')[:6]
    return render(request, 'home.html', {
        'popular_products': popular_products
    })

@login_required
def product_list(request):
    products = Product.objects.all()
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)
    return render(request, 'products/product_list.html', {'products': products})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, product=product).exists()
    return render(request, 'products/product_detail.html', {
        'product': product,
        'is_liked': is_liked,
    })


@login_required
def toggle_like(request, pk):
    product = get_object_or_404(Product, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, product=product)
    if not created:
        like.delete()
    return redirect('products:product_detail', pk=pk)


@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        return redirect('home')

    products = Product.objects.filter(seller=request.user)
    return render(request, 'products/seller_dashboard.html', {'products': products})


@login_required
def add_product(request):
    if request.user.role != 'seller':
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('products:seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})


@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Проверяем, что текущий пользователь - владелец товара
    if request.user != product.seller:
        messages.error(request, "You don't have permission to edit this product.")
        return redirect('products:product_detail', pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products:product_detail', pk=pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product
    })


@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    # Проверяем, что текущий пользователь - владелец товара
    if request.user != product.seller:
        messages.error(request, "You don't have permission to delete this product.")
        return redirect('products:product_detail', pk=pk)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('products:seller_dashboard')

    return render(request, 'products/delete_product.html', {'product': product})

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    # Проверка, что пользователь авторизован
    if request.method == 'POST':
        if request.user.is_authenticated:
            message = request.POST.get('message')

            send_mail(
                subject=f"📩 Freshmart | Новое сообщение от {request.user.username}",
                message=f"""
            Здравствуйте!

            Вы получили новое сообщение через форму обратной связи на сайте Freshmart.

            👤 Пользователь: {request.user.username}
            📧 Email: {request.user.email}

            💬 Сообщение:
            {message.strip()}

            ────────────────────────────
            С уважением, команда Freshmart
            freshmart.kz
            """,
                from_email=request.user.email,
                recipient_list=['khanekshakh@gmail.com'],
            )

            messages.success(request, "Сообщение успешно отправлено!")
        else:
            messages.error(request, "Вы должны быть авторизованы для отправки сообщения.")

    return render(request, 'contact.html')

