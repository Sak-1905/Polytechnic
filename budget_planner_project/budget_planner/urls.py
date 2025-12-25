from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Transactions
    path('transactions/', views.transactions, name='transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transactions/<int:pk>/delete/', views.delete_transaction, name='delete_transaction'),
    
    # Categories
    path('categories/', views.categories, name='categories'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:pk>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    
    # Budget Goals
    path('budget-goals/', views.budget_goals, name='budget_goals'),
    path('budget-goals/add/', views.add_budget_goal, name='add_budget_goal'),
    path('budget-goals/<int:pk>/edit/', views.edit_budget_goal, name='edit_budget_goal'),
    path('budget-goals/<int:pk>/delete/', views.delete_budget_goal, name='delete_budget_goal'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
]
