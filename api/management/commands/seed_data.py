# seed_data.py

from django.core.management.base import BaseCommand
from api.models import Role, User

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **kwargs):
        # Seed roles
        roles = ['Admin', 'User']
        for role_name in roles:
            Role.objects.create(name=role_name)

        # Seed users with roles
        admin_role = Role.objects.get(name='Admin')
        user_role = Role.objects.get(name='User')

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
