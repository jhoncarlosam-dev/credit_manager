from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Extiende el modelo User de Django para añadir roles.
    """
    class Role(models.TextChoices):
        ANALYST = 'analyst', 'Analista'
        VIEWER = 'viewer', 'Visualizador'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.VIEWER)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_analyst(self):
        return self.role == self.Role.ANALYST

# Señal para crear/guardar el perfil automáticamente cuando se crea un User
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()