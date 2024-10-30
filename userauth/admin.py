# userauth/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.contrib import messages
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )

    def delete_queryset(self, request, queryset):
        """
        Handles deletion of multiple users in the admin interface.
        """
        try:
            with transaction.atomic():  # Ensures all deletions occur within a transaction
                queryset.delete()
        except ProtectedError:
            messages.error(request, "Cannot delete some users because of related protected objects.")
    
    def delete_model(self, request, obj):
        """
        Handles deletion of a single user in the admin interface.
        """
        try:
            with transaction.atomic():
                obj.delete()
        except ProtectedError:
            messages.error(request, "Cannot delete this user due to related protected objects.")

admin.site.register(CustomUser, CustomUserAdmin)

from django.apps import AppConfig

class UserAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userauth'

    def ready(self):
        import userauth.signals  # Register signals