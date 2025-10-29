# ranking/apps.py
from django.apps import AppConfig

class RankingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ranking'

    def ready(self):
        from django.db.models.signals import post_save
        from django.contrib.auth import get_user_model
        from django.dispatch import receiver
        from .models import Profile

        User = get_user_model()

        @receiver(post_save, sender=User)
        def create_profile(sender, instance, created, **kwargs):
            if created:
                Profile.objects.get_or_create(user=instance)
