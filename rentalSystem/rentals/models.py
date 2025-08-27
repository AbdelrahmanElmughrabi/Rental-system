from django.db import models


class Rental(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_RETURNED = 'returned'
    STATUS_OVERDUE = 'overdue'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_RETURNED, 'Returned'),
        (STATUS_OVERDUE, 'Overdue'),
    ]

    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='rentals', null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='created_rentals', null=True, blank=True)
    customer_name = models.CharField(max_length=120)
    start_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        return f"Rental #{self.id} - {self.customer_name}"


class RentalItem(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey('inventory.Item', on_delete=models.PROTECT, related_name='rental_items')
    qty = models.IntegerField(default=1)
    per_day = models.DecimalField(max_digits=10, decimal_places=2)
    returned_qty = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.item.name} x{self.qty} in Rental #{self.rental.id}"


class ReturnReport(models.Model):
    rental_item = models.ForeignKey(RentalItem, on_delete=models.CASCADE, related_name='return_reports')
    returned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    damage_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"Return Report for {self.rental_item.item.name}"
