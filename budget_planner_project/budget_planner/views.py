from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from .models import Category, Transaction, BudgetGoal
from .forms import RegisterForm, CategoryForm, TransactionForm, BudgetGoalForm
import json
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create default categories for new user
            default_categories = [
                {'name': 'Salary', 'type': 'income', 'icon': 'bi-cash', 'color': 'success'},
                {'name': 'Freelance', 'type': 'income', 'icon': 'bi-briefcase', 'color': 'info'},
                {'name': 'Food & Dining', 'type': 'expense', 'icon': 'bi-cup-hot', 'color': 'warning'},
                {'name': 'Transportation', 'type': 'expense', 'icon': 'bi-car-front', 'color': 'primary'},
                {'name': 'Shopping', 'type': 'expense', 'icon': 'bi-cart', 'color': 'danger'},
                {'name': 'Bills & Utilities', 'type': 'expense', 'icon': 'bi-house', 'color': 'secondary'},
                {'name': 'Entertainment', 'type': 'expense', 'icon': 'bi-controller', 'color': 'info'},
                {'name': 'Healthcare', 'type': 'expense', 'icon': 'bi-heart-pulse', 'color': 'danger'},
            ]
            for cat in default_categories:
                Category.objects.create(user=user, **cat)
            
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    today = timezone.now()
    current_month = today.month
    current_year = today.year
    
    # Get monthly totals
    monthly_income = Transaction.objects.filter(
        user=request.user, type='income',
        date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_expense = Transaction.objects.filter(
        user=request.user, type='expense',
        date__month=current_month, date__year=current_year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    balance = monthly_income - monthly_expense
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user)[:5]
    
    # Budget goals progress
    budget_goals = BudgetGoal.objects.filter(
        user=request.user, month=current_month, year=current_year
    )
    
    # Expense by category for chart
    expense_by_category = Transaction.objects.filter(
        user=request.user, type='expense',
        date__month=current_month, date__year=current_year
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    # Monthly trend data (last 6 months)
    monthly_data = []
    for i in range(5, -1, -1):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        income = Transaction.objects.filter(
            user=request.user, type='income',
            date__month=month, date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            user=request.user, type='expense',
            date__month=month, date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        month_name = datetime(year, month, 1).strftime('%b')
        monthly_data.append({
            'month': month_name,
            'income': float(income),
            'expense': float(expense)
        })
    
    context = {
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'budget_goals': budget_goals,
        'expense_by_category': list(expense_by_category),
        'monthly_data': json.dumps(monthly_data),
        'current_month': today.strftime('%B %Y'),
    }
    return render(request, 'dashboard.html', context)


@login_required
def transactions(request):
    transaction_list = Transaction.objects.filter(user=request.user)
    
    # Filter by type
    trans_type = request.GET.get('type')
    if trans_type in ['income', 'expense']:
        transaction_list = transaction_list.filter(type=trans_type)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        transaction_list = transaction_list.filter(category_id=category_id)
    
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'transactions': transaction_list,
        'categories': categories,
        'selected_type': trans_type,
        'selected_category': category_id,
    }
    return render(request, 'transactions.html', context)


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transactions')
    else:
        form = TransactionForm(request.user)
    
    return render(request, 'transaction_form.html', {'form': form, 'title': 'Add Transaction'})


@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transactions')
    else:
        form = TransactionForm(request.user, instance=transaction)
    
    return render(request, 'transaction_form.html', {'form': form, 'title': 'Edit Transaction'})


@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
    return redirect('transactions')


@login_required
def categories(request):
    category_list = Category.objects.filter(user=request.user)
    return render(request, 'categories.html', {'categories': category_list})


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('categories')
    else:
        form = CategoryForm()

    return render(request, 'categories_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'categories_form.html', {'form': form, 'title': 'Edit Category'})


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
    return redirect('categories')


@login_required
def budget_goals(request):
    today = timezone.now()
    goals = BudgetGoal.objects.filter(user=request.user, month=today.month, year=today.year)
    return render(request, 'budget_goal.html', {
        'goals': goals,
        'current_month': today.strftime('%B %Y')
    })


@login_required
def add_budget_goal(request):
    if request.method == 'POST':
        form = BudgetGoalForm(request.user, request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            # Check if goal already exists
            existing = BudgetGoal.objects.filter(
                user=request.user,
                category=goal.category,
                month=goal.month,
                year=goal.year
            ).first()
            if existing:
                messages.error(request, 'A budget goal for this category and month already exists!')
            else:
                goal.save()
                messages.success(request, 'Budget goal added successfully!')
                return redirect('budget_goals')
    else:
        today = timezone.now()
        form = BudgetGoalForm(request.user, initial={'month': today.month, 'year': today.year})
    
    return render(request, 'budget_goal_form.html', {'form': form, 'title': 'Add Budget Goal'})


@login_required
def edit_budget_goal(request, pk):
    goal = get_object_or_404(BudgetGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetGoalForm(request.user, request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget goal updated successfully!')
            return redirect('budget_goals')
    else:
        form = BudgetGoalForm(request.user, instance=goal)
    
    return render(request, 'budget_goal_form.html', {'form': form, 'title': 'Edit Budget Goal'})


@login_required
def delete_budget_goal(request, pk):
    goal = get_object_or_404(BudgetGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Budget goal deleted successfully!')
    return redirect('budget_goals')


@login_required
def reports(request):
    today = timezone.now()
    year = int(request.GET.get('year', today.year))
    
    # Yearly summary
    yearly_income = Transaction.objects.filter(
        user=request.user, type='income', date__year=year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    yearly_expense = Transaction.objects.filter(
        user=request.user, type='expense', date__year=year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Monthly breakdown
    monthly_breakdown = []
    for month in range(1, 13):
        income = Transaction.objects.filter(
            user=request.user, type='income',
            date__month=month, date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        expense = Transaction.objects.filter(
            user=request.user, type='expense',
            date__month=month, date__year=year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_breakdown.append({
            'month': datetime(year, month, 1).strftime('%B'),
            'income': float(income),
            'expense': float(expense),
            'savings': float(income - expense)
        })
    
    # Category breakdown
    category_breakdown = Transaction.objects.filter(
        user=request.user, type='expense', date__year=year
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Convert Decimal objects to floats for JSON serialization
    category_breakdown_list = []
    for item in category_breakdown:
        category_breakdown_list.append({
            'category__name': item['category__name'],
            'category__color': item['category__color'],
            'total': float(item['total']) if item['total'] else 0.0
        })

    context = {
        'year': year,
        'years': range(2020, today.year + 2),
        'yearly_income': yearly_income,
        'yearly_expense': yearly_expense,
        'yearly_savings': yearly_income - yearly_expense,
        'monthly_breakdown': monthly_breakdown,
        'monthly_breakdown_json': json.dumps(monthly_breakdown),
        'category_breakdown': category_breakdown_list,
        'category_breakdown_json': json.dumps(category_breakdown_list),
    }
    return render(request, 'reports.html', context)


def about(request):
    """Display the About page"""
    return render(request, 'about.html')


def contact(request):
    """Display contact form and handle email submission"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Validate form data
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'contact.html')
        
        # Compose email
        full_message = f"""
        New Contact Form Submission
        
        From: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message}
        """
        
        try:
            # Check if email is properly configured
            if settings.EMAIL_HOST_PASSWORD == 'your-app-password-here':
                logger.error('Email not configured: EMAIL_HOST_PASSWORD is still set to placeholder')
                messages.error(request, 'Email service is not properly configured. Please contact the administrator.')
                return render(request, 'contact.html')
            
            # Send email
            send_mail(
                subject=f'Contact Form: {subject}',
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL_RECIPIENT],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('contact')
        except Exception as e:
            logger.error(f'Error sending contact email: {str(e)}')
            messages.error(request, f'Sorry, there was an error sending your message: {str(e)}')
            return render(request, 'contact.html')
    
    return render(request, 'contact.html')
