from django.contrib import admin
from .models import Rental, RentalItem, ReturnReport


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'store', 'customer_name', 'status', 'start_date', 'due_date', 'total')
    search_fields = ('customer_name', 'store__name')
    list_filter = ('store', 'status', 'start_date', 'due_date')
    readonly_fields = ('start_date',)


@admin.register(RentalItem)
class RentalItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'rental', 'item', 'qty', 'per_day', 'returned_qty')
    search_fields = ('rental__customer_name', 'item__name', 'item__sku')
    list_filter = ('rental__store',)


@admin.register(ReturnReport)
class ReturnReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'rental_item', 'returned_at', 'damage_cost')
    search_fields = ('rental_item__item__name', 'rental_item__rental__customer_name')
    list_filter = ('returned_at',)
    readonly_fields = ('returned_at',)
