from django.db import transaction
from django.utils import timezone


class RentalService:
    """Business actions for rentals."""

    @staticmethod
    @transaction.atomic
    def create_rental(*, item_id: int, customer_name: str, due_date):
        from inventory.models import Item
        from .models import Rental

        item = Item.objects.select_for_update().filter(id=item_id).first()
        if not item:
            raise ValueError("Item not found")
        if item.quantity < 1:
            raise ValueError("Insufficient inventory")

        rental = Rental.objects.create(
            item=item,
            customer_name=customer_name,
            due_date=due_date,
        )
        item.quantity -= 1
        item.save(update_fields=["quantity", "updated_at"])
        return rental

    @staticmethod
    @transaction.atomic
    def return_rental(*, rental_id: int, returned_at=None):
        from inventory.models import Item
        from .models import Rental

        rental = Rental.objects.select_for_update().filter(id=rental_id).select_related("item").first()
        if not rental:
            raise ValueError("Rental not found")
        if rental.status == Rental.STATUS_RETURNED:
            raise ValueError("Rental already returned")

        rental.returned_at = returned_at or timezone.now()
        rental.status = Rental.STATUS_RETURNED
        rental.save(update_fields=["returned_at", "status"])

        item: Item = rental.item
        item.quantity += 1
        item.save(update_fields=["quantity", "updated_at"])
        return rental
