class InventoryService:
    """Business actions for inventory."""

    @staticmethod
    def create_item(*, name: str, sku: str, price, description: str = "", quantity: int = 0, is_active: bool = True):
        from .models import Item
        item = Item.objects.create(
            name=name,
            sku=sku,
            price=price,
            description=description or "",
            quantity=quantity or 0,
            is_active=is_active,
        )
        return item

    @staticmethod
    def update_item(*, item, **fields):
        for key, value in fields.items():
            setattr(item, key, value)
        item.save()
        return item
