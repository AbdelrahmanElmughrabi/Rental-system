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

    item = models.ForeignKey('inventory.Item', on_delete=models.PROTECT, related_name='rentals')
    customer_name = models.CharField(max_length=120)
    rented_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    def __str__(self) -> str:
        return f"Rental #{self.id} - {self.item.sku} - {self.customer_name}"
