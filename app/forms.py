from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Product, Order, Review


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
    username = forms.CharField(label='Логин')
    email = forms.EmailField(label='Электронная почта')
    first_name = forms.CharField(max_length=50, label='Имя')
    last_name = forms.CharField(max_length=50, label='Фамилия')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    is_seller = forms.BooleanField(required=False, label='Зарегистрироваться как мастер (продавец)')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user



class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(max_length=50, label='Имя')
    last_name = forms.CharField(max_length=50, label='Фамилия')
    username = forms.CharField(max_length=150, label='Отображаемое имя')
    email = forms.EmailField(label='E-mail')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')
    address = forms.CharField(max_length=255, required=False, label='Адрес проживания')


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'price', 'material', 'dimensions', 'description', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = 'Выберите категорию'

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if not price or price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля.')
        return price

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Размер файла не должен превышать 5 МБ.')
        return image



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone', 'address']


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=[(5, '5 — Отлично'), (4, '4 — Хорошо'), (3, '3 — Нормально'), (2, '2 — Плохо'), (1, '1 — Ужасно')], label='Оценка')
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), label='Комментарий')

    class Meta:
        model = Review
        fields = ['rating', 'comment']
