from django.db import transaction
from .models import Item, InventoryTransaction


class InventoryService:
    """Business actions for inventory."""
    
    # Constants for transaction reasons
    REASON_RENTAL = 'rental'
    REASON_SALE = 'sale'
    REASON_RETURN = 'return'
    REASON_ADJUSTMENT = 'adjustment'
    REASON_INITIAL = 'initial'

    @staticmethod
    def create_item(*, store, category=None, name: str, sku: str, price, description: str = "", 
                   quantity: int = 0, is_rentable: bool = True, is_sellable: bool = True, 
                   rental_rate=None, status: str = 'active'):
        item = Item.objects.create(
            store=store,
            category=category,
            name=name,
            sku=sku,
            price=price,
            description=description or "",
            quantity=quantity or 0,
            is_rentable=is_rentable,
            is_sellable=is_sellable,
            rental_rate=rental_rate,
            status=status,
        )
        
        # Create initial transaction if quantity > 0
        if quantity > 0:
            InventoryTransaction.objects.create(
                item=item,
                delta=quantity,
                reason=InventoryTransaction.REASON_INITIAL,
                actor=None
            )
        
        return item

    @staticmethod
    def update_item(*, item, **fields):
        for key, value in fields.items():
            setattr(item, key, value)
        item.save()
        return item

    @staticmethod
    @transaction.atomic
    def adjust_stock(*, item: Item, delta: int, reason: str, actor=None):
        """
        Adjust item stock and create transaction record with row-level locking.
        
        Args:
            item: Item instance
            delta: Positive for additions, negative for reductions
            reason: One of InventoryTransaction.REASON_* choices
            actor: User performing the action (optional)
        """
        if reason not in dict(InventoryTransaction.REASON_CHOICES):
            raise ValueError(f"Invalid reason: {reason}")
        
        # Lock the item row to prevent race conditions
        locked_item = Item.objects.select_for_update().get(id=item.id)
        
        # Check if reduction would result in negative stock
        if delta < 0 and locked_item.quantity + delta < 0:
            raise ValueError(f"Insufficient stock. Current: {locked_item.quantity}, requested reduction: {abs(delta)}")
        
        # Update item quantity
        locked_item.quantity += delta
        locked_item.save(update_fields=['quantity', 'updated_at'])
        
        # Create transaction record
        transaction_record = InventoryTransaction.objects.create(
            item=locked_item,
            delta=delta,
            reason=reason,
            actor=actor
        )
        
        return transaction_record
