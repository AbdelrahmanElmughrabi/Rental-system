from typing import Optional

from django.db.models import Q, QuerySet


def get_item_by_id(*, store, item_id: int):
    from .models import Item
    return Item.objects.filter(store=store, id=item_id).first()


def list_items(*, store, search: Optional[str] = None, is_rentable: Optional[bool] = None, 
               is_sellable: Optional[bool] = None, status: Optional[str] = None, 
               category: Optional[int] = None) -> QuerySet:
    from .models import Item
    qs = Item.objects.filter(store=store).order_by('-created_at')
    
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    if is_rentable is not None:
        qs = qs.filter(is_rentable=is_rentable)
    if is_sellable is not None:
        qs = qs.filter(is_sellable=is_sellable)
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category_id=category)
    
    return qs


def get_category_by_id(*, store, category_id: int):
    from .models import Category
    return Category.objects.filter(store=store, id=category_id).first()


def list_categories(*, store, search: Optional[str] = None) -> QuerySet:
    from .models import Category
    qs = Category.objects.filter(store=store).order_by('name')
    
    if search:
        qs = qs.filter(name__icontains=search)
    
    return qs


def get_low_stock_items(*, store, threshold: int = 5) -> QuerySet:
    """Get items with quantity below threshold."""
    from .models import Item
    return Item.objects.filter(
        store=store,
        quantity__lt=threshold,
        status='active'
    ).order_by('quantity')


def get_item_transactions(*, item, limit: Optional[int] = None) -> QuerySet:
    """Get transaction history for a specific item."""
    from .models import InventoryTransaction
    qs = InventoryTransaction.objects.filter(item=item).order_by('-created_at')
    
    if limit:
        qs = qs[:limit]
    
    return qs
