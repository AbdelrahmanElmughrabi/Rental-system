from datetime import date
from typing import Optional

from django.db.models import QuerySet


def get_rental_by_id(*, store, rental_id: int):
    from .models import Rental
    return Rental.objects.filter(store=store, id=rental_id).select_related('store').first()


def list_rentals(*, store, status: Optional[str] = None, item_id: Optional[int] = None,
                 date_from: Optional[date] = None, date_to: Optional[date] = None) -> QuerySet:
    from .models import Rental

    qs = Rental.objects.filter(store=store).select_related('store').order_by('-start_date')
    if status:
        qs = qs.filter(status=status)
    if item_id:
        qs = qs.filter(items__item_id=item_id)
    if date_from:
        qs = qs.filter(start_date__date__gte=date_from)
    if date_to:
        qs = qs.filter(start_date__date__lte=date_to)
    return qs


def get_rentals_due_today(*, store) -> QuerySet:
    """Get rentals due for return today."""
    from .models import Rental
    from django.utils import timezone
    
    today = timezone.now().date()
    return Rental.objects.filter(
        store=store,
        due_date=today,
        status=Rental.STATUS_ACTIVE
    ).select_related('store')


def get_active_rentals(*, store) -> QuerySet:
    """Get currently active rentals."""
    from .models import Rental
    
    return Rental.objects.filter(
        store=store,
        status=Rental.STATUS_ACTIVE
    ).select_related('store')
