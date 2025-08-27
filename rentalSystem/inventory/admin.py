from django.contrib import admin
from .models import Category, Item, ItemImage, InventoryTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'store')
    search_fields = ('name', 'store__name')
    list_filter = ('store',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sku', 'store', 'category', 'quantity', 'price', 'status')
    search_fields = ('name', 'sku', 'store__name')
    list_filter = ('store', 'category', 'is_rentable', 'is_sellable', 'status')
    prepopulated_fields = {'sku': ('name',)}


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'created_at')
    search_fields = ('item__name', 'item__sku')


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'delta', 'reason', 'actor', 'created_at')
    search_fields = ('item__name', 'item__sku', 'reason')
    list_filter = ('reason', 'created_at')
    readonly_fields = ('created_at',)
