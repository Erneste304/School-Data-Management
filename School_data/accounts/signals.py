from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, StaffProfile


@receiver(post_save, sender=CustomUser)
def create_staff_profile(sender, instance, created, **kwargs):
    """
    Automatically create a StaffProfile whenever a new staff user is saved.
    Public/visitor accounts do not get a profile.
    """
    if created and instance.role != CustomUser.Role.PUBLIC:
        StaffProfile.objects.get_or_create(user=instance)