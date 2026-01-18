from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Transaction, BudgetGoal

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CategoryForm(forms.ModelForm):
    ICON_CHOICES = [
        ('', '-- Select Icon --'),
        ('bi-house', 'House'),
        ('bi-car-front', 'Car'),
        ('bi-cart', 'Shopping'),
        ('bi-cup-hot', 'Food & Drink'),
        ('bi-heart-pulse', 'Health'),
        ('bi-mortarboard', 'Education'),
        ('bi-controller', 'Entertainment'),
        ('bi-briefcase', 'Work'),
        ('bi-piggy-bank', 'Savings'),
        ('bi-cash', 'Salary'),
        ('bi-gift', 'Gifts'),
        ('bi-three-dots', 'Other'),
    ]
    
    COLOR_CHOICES = [
        ('primary', 'Blue'),
        ('success', 'Green'),
        ('danger', 'Red'),
        ('warning', 'Yellow'),
        ('info', 'Cyan'),
        ('secondary', 'Gray'),
        ('dark', 'Dark'),
    ]
    
    icon = forms.ChoiceField(choices=ICON_CHOICES)
    color = forms.ChoiceField(choices=COLOR_CHOICES)
    
    class Meta:
        model = Category
        fields = ['name', 'type', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['icon'].widget.attrs['class'] = 'form-select'
        self.fields['color'].widget.attrs['class'] = 'form-select'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type', 'category', 'amount', 'description', 'date']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select', 'id': 'transaction-type'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)


class BudgetGoalForm(forms.ModelForm):
    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
        (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
        (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December'),
    ]
    
    month = forms.ChoiceField(choices=MONTH_CHOICES)
    
    class Meta:
        model = BudgetGoal
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2020', 'max': '2030'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user, type='expense')
        self.fields['month'].widget.attrs['class'] = 'form-select'
