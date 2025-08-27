from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "currency", "timezone")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
