from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from inventory.services import InventoryService


class RentalService:
    """Business actions for rentals."""

    @staticmethod
    @transaction.atomic
    def create_rental(*, store, created_by, customer_name: str, due_date, items):
        """
        Create a rental with multiple items and proper inventory management.
        
        Args:
            store: Store instance
            created_by: User creating the rental
            customer_name: Customer name
            due_date: Due date for the rental
            items: List of dicts with item_id, qty, per_day
        """
        from inventory.models import Item
        from .models import Rental, RentalItem
        
        # Validate due date
        if due_date <= timezone.now().date():
            raise ValidationError("Due date must be in the future")
        
        # Create rental
        rental = Rental.objects.create(
            store=store,
            created_by=created_by,
            customer_name=customer_name,
            due_date=due_date,
        )
        
        rental_items = []
        total_cost = 0
        
        # Process each item
        for item_data in items:
            item_id = item_data['item_id']
            qty = item_data.get('qty', 1)
            per_day = item_data.get('per_day', 0)
            
            # Get and lock item
            item = Item.objects.select_for_update().filter(
                id=item_id, 
                store=store,
                is_rentable=True,
                status='active'
            ).first()
            
            if not item:
                raise ValidationError(f"Item {item_id} not found or not rentable")
            
            if item.quantity < qty:
                raise ValidationError(f"Insufficient inventory for {item.name}. Available: {item.quantity}, requested: {qty}")
            
            # Create rental item
            rental_item = RentalItem.objects.create(
                rental=rental,
                item=item,
                qty=qty,
                per_day=per_day
            )
            rental_items.append(rental_item)
            
            # Calculate cost
            days = (due_date - timezone.now().date()).days
            total_cost += per_day * qty * days
            
            # Reduce inventory using service
            InventoryService.adjust_stock(
                item=item,
                delta=-qty,
                reason=InventoryService.REASON_RENTAL,
                actor=created_by
            )
        
        # Update rental total
        rental.total = total_cost
        rental.save(update_fields=['total'])
        
        return rental

    @staticmethod
    @transaction.atomic
    def process_return(*, rental_id: int, returned_items, returned_at=None):
        """
        Process rental return with partial returns support.
        
        Args:
            rental_id: Rental ID
            returned_items: List of dicts with rental_item_id, qty, condition, damage_cost
            returned_at: Return timestamp (defaults to now)
        """
        from .models import Rental, RentalItem, ReturnReport
        
        returned_at = returned_at or timezone.now()
        
        # Get and lock rental
        rental = Rental.objects.select_for_update().filter(id=rental_id).first()
        if not rental:
            raise ValidationError("Rental not found")
        
        if rental.status == Rental.STATUS_RETURNED:
            raise ValidationError("Rental already returned")
        
        # Process each returned item
        for return_data in returned_items:
            rental_item_id = return_data['rental_item_id']
            qty = return_data.get('qty', 1)
            condition = return_data.get('condition', 'good')
            damage_cost = return_data.get('damage_cost', 0)
            
            # Get rental item
            rental_item = RentalItem.objects.select_for_update().filter(
                id=rental_item_id,
                rental=rental
            ).first()
            
            if not rental_item:
                raise ValidationError(f"Rental item {rental_item_id} not found")
            
            if qty > rental_item.qty - rental_item.returned_qty:
                raise ValidationError(f"Cannot return more than rented. Rented: {rental_item.qty}, already returned: {rental_item.returned_qty}")
            
            # Update returned quantity
            rental_item.returned_qty += qty
            rental_item.save(update_fields=['returned_qty'])
            
            # Create return report
            ReturnReport.objects.create(
                rental_item=rental_item,
                returned_at=returned_at,
                notes=f"Condition: {condition}",
                damage_cost=damage_cost
            )
            
            # Return inventory using service
            InventoryService.adjust_stock(
                item=rental_item.item,
                delta=qty,
                reason=InventoryService.REASON_RETURN,
                actor=None  # Could be passed from request
            )
        
        # Check if all items are returned
        all_returned = all(
            item.returned_qty >= item.qty 
            for item in rental.items.all()
        )
        
        if all_returned:
            rental.returned_date = returned_at
            rental.status = Rental.STATUS_RETURNED
            rental.save(update_fields=['returned_date', 'status'])
        
        return rental
