from django.contrib import admin
from .models import User, StoreUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "email")
    list_filter = ("is_active", "is_staff", "is_superuser")


@admin.register(StoreUser)
class StoreUserAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "store", "role", "is_active")
    search_fields = ("user__username", "store__name", "role")
    list_filter = ("role", "is_active")
