import csv
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum, Avg, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .forms import RegisterForm, ProfileUpdateForm, ProductForm, OrderForm, ReviewForm
from .models import Master, Showcase, Category, Product, Order, OrderItem, Review, MasterPayout, Favorite


def home(request):
    categories = Category.objects.all()[:3]
    jewelry_products = Product.objects.select_related('category', 'showcase__master').order_by('-created_at')[:4]
    stats = {
        'masters_count': Master.objects.filter(is_seller=True).count(),
        'products_count': Product.objects.count(),
        'orders_count': Order.objects.count(),
        'avg_rating': Master.objects.filter(is_seller=True).aggregate(Avg('rating'))['rating__avg'] or 0,
    }
    return render(request, 'home.html', {
        'categories': categories,
        'jewelry_products': jewelry_products,
        'stats': stats,
    })


def catalog(request):
    products = Product.objects.select_related('category', 'showcase__master').all()
    categories = Category.objects.all()

    q = request.GET.get('q', '').strip()
    cat_slug = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    material = request.GET.get('material', '').strip()
    sort = request.GET.get('sort', '-created_at')

    if q:
        products = products.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if cat_slug:
        products = products.filter(category__slug=cat_slug)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if material:
        products = products.filter(material__icontains=material)

    allowed_sorts = ['price', '-price', '-created_at', 'title']
    if sort in allowed_sorts:
        products = products.order_by(sort)

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'catalog.html', {
        'page_obj': page_obj,
        'categories': categories,
        'q': q,
        'cat_slug': cat_slug,
        'min_price': min_price,
        'max_price': max_price,
        'material': material,
        'sort': sort,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related('showcase__master__user', 'category'), pk=pk)
    reviews = product.reviews.select_related('author').order_by('-created_at')
    is_fav = False
    if request.user.is_authenticated:
        is_fav = Favorite.objects.filter(user=request.user, product=product).exists()

    review_form = ReviewForm()
    order_form = OrderForm(initial={'full_name': request.user.get_full_name()} if request.user.is_authenticated else None)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Войдите в аккаунт, чтобы выполнить это действие.')
            return redirect('login')

        if 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                rev = review_form.save(commit=False)
                rev.product = product
                rev.author = request.user
                rev.save()
                messages.success(request, 'Спасибо! Ваш отзыв опубликован, рейтинг мастера обновлён.')
                return redirect('product_detail', pk=product.pk)

        elif 'submit_order' in request.POST:
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                with transaction.atomic():
                    order = order_form.save(commit=False)
                    order.buyer = request.user
                    order.total_amount = product.price
                    order.commission_amount = round(product.price * Decimal('0.10'), 2)
                    order.save()
                    OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)
                    MasterPayout.objects.create(
                        master=product.showcase.master,
                        order=order,
                        gross_amount=order.total_amount,
                        commission=order.commission_amount,
                        net_payout=order.total_amount - order.commission_amount,
                    )
                    send_mail(
                        subject=f'Новый заказ №{order.id} в Мастерской',
                        message=f'Оформлен заказ на изделие "{product.title}" на сумму {order.total_amount} руб.',
                        from_email='noreply@masterskaya.ru',
                        recipient_list=[request.user.email or 'user@example.com'],
                        fail_silently=True,
                    )
                messages.success(request, f'Заказ №{order.id} успешно оформлен!')
                return redirect('profile')

    return render(request, 'product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'order_form': order_form,
        'is_fav': is_fav,
    })


@login_required
def product_create(request):
    master, _ = Master.objects.get_or_create(user=request.user)
    if not master.is_seller:
        master.is_seller = True
        master.save()
    showcase, _ = Showcase.objects.get_or_create(master=master, defaults={'title': f'Витрина {request.user.username}'})

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.showcase = showcase
            prod.save()
            messages.success(request, 'Изделие успешно добавлено в каталог!')
            return redirect('product_detail', pk=prod.pk)
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {'form': form, 'is_edit': False})


@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.showcase.master.user != request.user and not request.user.is_staff:
        messages.error(request, 'У вас нет прав для редактирования чужого изделия.')
        return redirect('catalog')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены.')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_form.html', {'form': form, 'is_edit': True, 'product': product})


@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.showcase.master.user == request.user or request.user.is_staff:
        product.delete()
        messages.success(request, 'Изделие удалено.')
    else:
        messages.error(request, 'Нет прав на удаление.')
    return redirect('profile')


@login_required
def profile(request):
    master, _ = Master.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            master.phone = form.cleaned_data['phone']
            master.address = form.cleaned_data['address']
            master.save()
            messages.success(request, 'Данные профиля обновлены!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'username': request.user.username,
            'email': request.user.email,
            'phone': master.phone,
            'address': master.address,
        })

    my_orders = Order.objects.filter(buyer=request.user).prefetch_related('items__product').order_by('-created_at')
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    my_products = Product.objects.filter(showcase__master=master).order_by('-created_at') if master.is_seller else []
    payouts = MasterPayout.objects.filter(master=master).select_related('order').order_by('-created_at') if master.is_seller else []
    payout_summary = payouts.aggregate(
        total_sales=Sum('gross_amount'),
        total_comm=Sum('commission'),
        total_net=Sum('net_payout'),
        count=Count('id')
    ) if master.is_seller else {}

    return render(request, 'profile.html', {
        'form': form,
        'master': master,
        'my_orders': my_orders,
        'favorites': favorites,
        'my_products': my_products,
        'payouts': payouts,
        'payout_summary': payout_summary,
    })


@login_required
def toggle_favorite(request, pk):
    product = get_object_or_404(Product, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        fav.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'count': Favorite.objects.filter(user=request.user).count()})


@login_required
def export_payouts_csv(request):
    master = get_object_or_404(Master, user=request.user)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="payouts_report.csv"'
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Номер заказа', 'Дата', 'Сумма продажи (руб)', 'Комиссия площадки 10% (руб)', 'К выплате мастеру (руб)'])
    for p in MasterPayout.objects.filter(master=master).select_related('order'):
        writer.writerow([p.order.id, p.created_at.strftime('%d.%m.%Y'), p.gross_amount, p.commission, p.net_payout])
    return response

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            is_seller = form.cleaned_data.get('is_seller', False)
            master = Master.objects.create(user=user, is_seller=is_seller)
            if is_seller:
                Showcase.objects.create(master=master, title=f'Мастерская {user.username}')
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('profile')
    else:
        form = RegisterForm()
    return render(request, 'auth.html', {
        'form': form,
        'title': 'Регистрация',
        'btn_text': 'Создать аккаунт',
        'is_register': True,
    })



def about(request):
    return render(request, 'about.html')
