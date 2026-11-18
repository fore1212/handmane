import random
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from app.models import Master, Showcase, Category, Product, Order, OrderItem, Review, MasterPayout


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными (30+ товаров)'

    def handle(self, *args, **kwargs):
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@mail.ru', 'is_staff': True, 'is_superuser': True})
        admin_user.set_password('admin123')
        admin_user.save()

        cat_data = [
            ('Украшения', 'jewelry'),
            ('Предметы интерьера', 'interior'),
            ('Свечи', 'candles'),
            ('Керамика', 'ceramics'),
        ]
        categories = [Category.objects.get_or_create(slug=s, defaults={'name': n})[0] for n, s in cat_data]

        masters = []
        for i in range(1, 6):
            u, _ = User.objects.get_or_create(username=f'master{i}', defaults={'first_name': f'Мастер_{i}', 'email': f'm{i}@mail.ru'})
            u.set_password('pass12345')
            u.save()
            m, _ = Master.objects.get_or_create(user=u, defaults={'is_seller': True, 'phone': f'+7900111223{i}', 'bio': 'Авторская мастерская ручной работы'})
            Showcase.objects.get_or_create(master=m, defaults={'title': f'Мастерская №{i}', 'description': 'Изделия с душой и вниманием к деталям'})
            masters.append(m)

        titles = [
            'Брошь с цветным стеклом', 'Колье ручной работы', 'Красивая новогодняя брошь', 'Серебряная цепочка',
            'Вязаный венок для дома', 'Глиняная кружка Лес', 'Ароматическая соевая свеча', 'Шкатулка с росписью',
            'Браслет из натуральных камней', 'Керамическая ваза ручной лепки', 'Кольцо с лунным камнем', 'Подвеска Лист'
        ]
        materials = ['Серебро, стекло', 'Керамика, глазурь', 'Соевый воск, дерево', 'Хлопок, лён', 'Натуральные камни']

        products = []
        for i in range(1, 35):
            title = f'{random.choice(titles)} #{i}'
            p, _ = Product.objects.get_or_create(
                title=title,
                defaults={
                    'showcase': random.choice(masters).showcase,
                    'category': random.choice(categories),
                    'description': f'Уникальное изделие ручной работы ({title}). Создано с любовью в единственном экземпляре.',
                    'price': Decimal(random.randint(8, 60) * 100),
                    'material': random.choice(materials),
                    'dimensions': f'{random.randint(5, 25)} x {random.randint(5, 25)} см',
                }
            )
            products.append(p)

        buyer, _ = User.objects.get_or_create(username='buyer1', defaults={'first_name': 'Анна', 'last_name': 'Иванова', 'email': 'buyer@mail.ru'})
        buyer.set_password('pass12345')
        buyer.save()
        Master.objects.get_or_create(user=buyer, defaults={'is_seller': False, 'phone': '+79998887766', 'address': 'г. Ульяновск, ул. Ленина, 1'})

        for i in range(1, 13):
            prod = random.choice(products)
            total = prod.price
            comm = round(total * Decimal('0.10'), 2)
            order = Order.objects.create(
                buyer=buyer, full_name='Иванова Анна', phone='+79998887766',
                address='г. Ульяновск, ул. Гончарова, 10', status='completed',
                total_amount=total, commission_amount=comm
            )
            OrderItem.objects.create(order=order, product=prod, quantity=1, price=prod.price)
            MasterPayout.objects.create(master=prod.showcase.master, order=order, gross_amount=total, commission=comm, net_payout=total - comm)
            Review.objects.create(product=prod, author=buyer, rating=random.randint(4, 5), comment='Отличное качество, очень красивая работа!')

