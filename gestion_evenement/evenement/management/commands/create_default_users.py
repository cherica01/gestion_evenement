from django.core.management.base import BaseCommand
from evenement.models import CustomUser

class Command(BaseCommand):
    help = "Crée des utilisateurs par défaut"

    def handle(self, *args, **kwargs):
        users_data = [
            {'username': 'organisateur1', 'role': 'organisateur', 'password': 'password123'},
            {'username': 'participant1', 'role': 'participant', 'password': 'password123'},
        ]

        for user_data in users_data:
            user, created = CustomUser.objects.get_or_create(username=user_data['username'])
            if created:
                user.set_password(user_data['password'])
                user.role = user_data['role']
                user.save()
                self.stdout.write(f"Utilisateur {user.username} créé avec le rôle {user.role}")
            else:
                self.stdout.write(f"Utilisateur {user.username} existe déjà")
