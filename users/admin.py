from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'is_staff', 'is_active', 'email_verified') 

admin.site.register(CustomUser, CustomUserAdmin)

class CustomUserAdmin(UserAdmin):
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser  

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  

    list_display = ("username", "email", "is_staff", "is_active", "date_joined")  # Show these fields in the list
    search_fields = ("username", "email")  # Allow searching by username or email
    list_filter = ("is_staff", "is_superuser", "is_active")  # Add filter options

if admin.site.is_registered(User):
    admin.site.unregister(User)
if not admin.site.is_registered(CustomUser):
    class CustomUserAdmin(UserAdmin):
        list_display = ("username", "email", "is_staff", "is_active", "date_joined")

    admin.site.register(CustomUser, CustomUserAdmin) 
