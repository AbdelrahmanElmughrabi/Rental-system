from django.db import models


class Category(models.Model):
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='categories', null=True, blank=True)
    name = models.CharField(max_length=120)

    class Meta:
        unique_together = [('store', 'name')]
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return f"{self.name} ({self.store.name if self.store else 'No Store'})"


class Item(models.Model):
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    is_rentable = models.BooleanField(default=True)
    is_sellable = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rental_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(default=0)
    status = models.CharField(max_length=16, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('store', 'sku')]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='item_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Image for {self.item.name}"


class InventoryTransaction(models.Model):
    REASON_RENTAL = 'rental'
    REASON_SALE = 'sale'
    REASON_RETURN = 'return'
    REASON_ADJUSTMENT = 'adjustment'
    REASON_INITIAL = 'initial'

    REASON_CHOICES = [
        (REASON_RENTAL, 'Rental'),
        (REASON_SALE, 'Sale'),
        (REASON_RETURN, 'Return'),
        (REASON_ADJUSTMENT, 'Adjustment'),
        (REASON_INITIAL, 'Initial'),
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transactions')
    delta = models.IntegerField(help_text='Positive for additions, negative for reductions')
    reason = models.CharField(max_length=16, choices=REASON_CHOICES)
    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.item.name}: {self.delta} ({self.reason})"
