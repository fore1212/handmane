from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import LoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('product/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('profile/', views.profile, name='profile'),
    path('profile/export-csv/', views.export_payouts_csv, name='export_payouts_csv'),
    path('about/', views.about, name='about'),
path('login/', auth_views.LoginView.as_view(template_name='auth.html', authentication_form=LoginForm, extra_context={'title': 'Вход в аккаунт', 'btn_text': 'Войти', 'is_register': False}), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
]
