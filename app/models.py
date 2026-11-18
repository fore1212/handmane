from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg


class Master(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master_profile', verbose_name='Пользователь')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    bio = models.TextField(blank=True, verbose_name='О себе')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name='Средний рейтинг')
    is_seller = models.BooleanField(default=False, verbose_name='Статус мастера')

    def update_rating(self):
        avg = Review.objects.filter(product__showcase__master=self).aggregate(Avg('rating'))['rating__avg']
        self.rating = round(avg, 2) if avg else 0.00
        self.save(update_fields=['rating'])

    def __str__(self):
        return self.user.username


class Showcase(models.Model):
    master = models.OneToOneField(Master, on_delete=models.CASCADE, related_name='showcase', verbose_name='Мастер')
    title = models.CharField(max_length=150, verbose_name='Название витрины')
    description = models.TextField(blank=True, verbose_name='Описание витрины')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    slug = models.SlugField(unique=True, verbose_name='URL-метка')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Фото категории')

    def __str__(self):
        return self.name


class Product(models.Model):
    showcase = models.ForeignKey(Showcase, on_delete=models.CASCADE, related_name='products', verbose_name='Витрина')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Категория')
    title = models.CharField(max_length=200, verbose_name='Название изделия')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    material = models.CharField(max_length=100, default='Ручная работа', verbose_name='Материал')
    dimensions = models.CharField(max_length=100, blank=True, verbose_name='Размеры / габариты')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='Главное фото')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    def __str__(self):
        return self.title


class ProductPhoto(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='photos', verbose_name='Изделие')
    image = models.ImageField(upload_to='products/gallery/', verbose_name='Дополнительное фото')


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В работе'),
        ('completed', 'Выполнен'),
    ]
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Покупатель')
    full_name = models.CharField(max_length=150, verbose_name='ФИО получателя')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.CharField(max_length=255, verbose_name='Адрес доставки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Сумма заказа')
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Комиссия площадки (10%)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')

    def __str__(self):
        return f'Заказ №{self.id} от {self.buyer.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Изделие')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена на момент заказа')


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name='Изделие')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name='Оценка')
    comment = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.showcase.master.update_rating()


class MasterPayout(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='payouts', verbose_name='Мастер')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма продажи')
    commission = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Комиссия площадки')
    net_payout = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='К выплате мастеру')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата начисления')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')
