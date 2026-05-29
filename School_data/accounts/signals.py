from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, StaffProfile, ParentProfile


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create appropriate profile based on user role.
    """
    if not created:
        return
    
    if instance.is_staff_member:
        # Create StaffProfile for staff members
        StaffProfile.objects.get_or_create(user=instance)
    
    elif instance.is_teacher:
        # Create both StaffProfile and TeacherProfile for teachers
        StaffProfile.objects.get_or_create(user=instance)
        from academics.models import TeacherProfile
        TeacherProfile.objects.get_or_create(
            user=instance,
            defaults={'hire_date': instance.created_at.date() if instance.created_at else None}
        )
    
    elif instance.is_parent:
        # Create ParentProfile for parents
        ParentProfile.objects.get_or_create(user=instance)