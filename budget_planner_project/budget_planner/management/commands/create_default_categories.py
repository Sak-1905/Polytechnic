from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from budget_planner.models import Category

class Command(BaseCommand):
    help = 'Create default categories for users who don\'t have any'

    def handle(self, *args, **options):
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

        users = User.objects.all()
        for user in users:
            existing_count = Category.objects.filter(user=user).count()
            if existing_count == 0:
                self.stdout.write(f'Creating default categories for user: {user.username}')
                for cat in default_categories:
                    Category.objects.create(user=user, **cat)
                self.stdout.write(self.style.SUCCESS(f'Created {len(default_categories)} categories for {user.username}'))
            else:
                self.stdout.write(f'User {user.username} already has {existing_count} categories')

        self.stdout.write(self.style.SUCCESS('Default categories creation completed'))
