from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from budget_planner.models import Category

class Command(BaseCommand):
    help = 'Create default categories for users'

    def handle(self, *args, **options):
        default_categories = [
            # Income categories
            {'name': 'Salary', 'type': 'income', 'icon': 'bi-cash', 'color': 'success'},
            {'name': 'Freelance', 'type': 'income', 'icon': 'bi-briefcase', 'color': 'info'},
            {'name': 'Gifts', 'type': 'income', 'icon': 'bi-gift', 'color': 'info'},
            
            # Expense categories
            {'name': 'House', 'type': 'expense', 'icon': 'bi-house', 'color': 'primary'},
            {'name': 'Car', 'type': 'expense', 'icon': 'bi-car-front', 'color': 'primary'},
            {'name': 'Shopping', 'type': 'expense', 'icon': 'bi-cart', 'color': 'danger'},
            {'name': 'Food & Drink', 'type': 'expense', 'icon': 'bi-cup-hot', 'color': 'warning'},
            {'name': 'Health', 'type': 'expense', 'icon': 'bi-heart-pulse', 'color': 'danger'},
            {'name': 'Education', 'type': 'expense', 'icon': 'bi-mortarboard', 'color': 'info'},
            {'name': 'Entertainment', 'type': 'expense', 'icon': 'bi-controller', 'color': 'secondary'},
            {'name': 'Work', 'type': 'expense', 'icon': 'bi-briefcase', 'color': 'dark'},
            {'name': 'Savings', 'type': 'expense', 'icon': 'bi-piggy-bank', 'color': 'success'},
            {'name': 'Other', 'type': 'expense', 'icon': 'bi-three-dots', 'color': 'secondary'},
        ]

        users = User.objects.all()
        created_count = 0
        
        for user in users:
            self.stdout.write(f'Processing user: {user.username}')
            for cat in default_categories:
                category, created = Category.objects.get_or_create(
                    user=user,
                    name=cat['name'],
                    defaults={
                        'type': cat['type'],
                        'icon': cat['icon'],
                        'color': cat['color']
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  Created: {cat["name"]}')
                else:
                    self.stdout.write(f'  Already exists: {cat["name"]}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} new categories'))
