from django.contrib import admin
from .models import Category, Transaction, BudgetGoal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'user', 'created_at']
    list_filter = ['type', 'user']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'type', 'amount', 'category', 'date', 'user']
    list_filter = ['type', 'category', 'date', 'user']
    search_fields = ['description']
    date_hierarchy = 'date'


@admin.register(BudgetGoal)
class BudgetGoalAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'month', 'year', 'user']
    list_filter = ['month', 'year', 'user']
