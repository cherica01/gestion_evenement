from django.db import models

from django.db import models


from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('participant', 'Participant'),
        ('organisateur', 'Organisateur'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='participant')

class Evenement(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    lieu = models.CharField(max_length=300)
    date = models.DateTimeField()
    capacite = models.PositiveIntegerField()
    programme = models.TextField()
    organisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evenements_organises'
    )
   
    def __str__(self):
        return self.titre

    def capacite_restante(self):
        return self.capacite - self.participants.count()

class Participant(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participations'
    )
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='participants')
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('utilisateur', 'evenement')

    def __str__(self):
        return f"{self.utilisateur.username} - {self.evenement.titre}"

class Notification(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    est_rappel = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        type_notification = "Rappel" if self.est_rappel else "Notification"
        return f"{type_notification} pour {self.evenement.titre}: {self.message[:30]}..."
