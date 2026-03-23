from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, StaffProfile


class StaffProfileInline(admin.StackedInline):
    model   = StaffProfile
    extra   = 0
    can_delete = False


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines       = [StaffProfileInline]
    list_display  = ['username', 'get_full_name', 'email', 'role', 'is_active', 'created_at']
    list_filter   = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering      = ['last_name', 'first_name']

    fieldsets = (
        (None,            {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'photo')}),
        ('Role & access', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Metadata',      {'fields': ('created_by', 'created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'employee_id', 'department', 'date_joined']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']