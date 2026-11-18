from django.contrib import admin
from .models import Master, Showcase, Category, Product, ProductPhoto, Order, OrderItem, Review, MasterPayout

admin.site.register([Master, Showcase, Category, Product, ProductPhoto, Order, OrderItem, Review, MasterPayout])
