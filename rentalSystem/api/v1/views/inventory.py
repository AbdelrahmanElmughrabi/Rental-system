from rest_framework import generics

from core.pagination import DefaultPagination
from inventory.models import Item
from ..serializers.inventory import (
    ItemSerializer,
    ItemCreateSerializer,
    ItemUpdateSerializer,
)


class ItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = Item.objects.all().order_by('-created_at')
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ItemCreateSerializer
        return ItemSerializer

    def get_queryset(self):
        from inventory.selectors import list_items

        search = self.request.query_params.get('search')
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() in ('1', 'true', 'yes')
        return list_items(search=search, is_active=is_active)


class ItemDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ItemUpdateSerializer
        return ItemSerializer 