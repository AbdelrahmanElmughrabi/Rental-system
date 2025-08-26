from typing import Optional

from django.db.models import Q, QuerySet


def get_item_by_id(*, item_id: int):
    from .models import Item
    return Item.objects.filter(id=item_id).first()


def list_items(*, search: Optional[str] = None, is_active: Optional[bool] = None) -> QuerySet:
    from .models import Item
    qs = Item.objects.all().order_by('-created_at')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs
