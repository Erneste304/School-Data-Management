from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to automatically create a Profile when a new CustomUser is created.
    """
    if created:
        # A default role can be set here if needed, e.g., 'STUDENT'.
        # However, it's often better to leave it null and have an admin assign it,
        # or handle it in the user creation form.
        Profile.objects.create(user=instance)