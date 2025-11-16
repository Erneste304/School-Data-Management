from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import CustomUser, Profile


@admin.action(description="Assign 'Can Create Announcement' permission to selected Admins/Heads")
def assign_announcement_permission(modeladmin, request, queryset):
    """
    Admin action to grant the 'can_create_announcement' permission to users
    with the 'ADMIN' or 'HEAD' role.
    """
    try:
        # Fetch the specific permission object
        permission = Permission.objects.get(codename='can_create_announcement')
    except Permission.DoesNotExist:
        modeladmin.message_user(request, "The 'can_create_announcement' permission was not found.", level='error')
        return

    updated_count = 0
    for user in queryset.filter(profile__role__in=['ADMIN', 'HEAD']):
        user.user_permissions.add(permission)
        updated_count += 1
    modeladmin.message_user(request, f"Successfully assigned permission to {updated_count} user(s).")

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    actions = [assign_announcement_permission]

admin.site.register(CustomUser, CustomUserAdmin)
# By managing the Profile via the inline in CustomUserAdmin,
# registering it separately is redundant and can be confusing.
# admin.site.register(Profile)
