from datetime import date
from typing import Optional

from django.db.models import QuerySet


def get_rental_by_id(*, rental_id: int):
    from .models import Rental
    return Rental.objects.filter(id=rental_id).select_related('item').first()


def list_rentals(*, status: Optional[str] = None, item_id: Optional[int] = None,
                 date_from: Optional[date] = None, date_to: Optional[date] = None) -> QuerySet:
    from .models import Rental

    qs = Rental.objects.all().select_related('item').order_by('-rented_at')
    if status:
        qs = qs.filter(status=status)
    if item_id:
        qs = qs.filter(item_id=item_id)
    if date_from:
        qs = qs.filter(rented_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(rented_at__date__lte=date_to)
    return qs
