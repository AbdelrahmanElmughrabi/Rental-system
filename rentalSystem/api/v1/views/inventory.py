from rest_framework import generics

from core.pagination import DefaultPagination
from core.mixins import TenancyMixin, IsStoreMember
from inventory.models import Item, Category
from ..serializers.inventory import (
    ItemSerializer,
    ItemCreateSerializer,
    ItemUpdateSerializer,
    CategorySerializer,
)


class CategoryListAPIView(TenancyMixin, generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = DefaultPagination
    permission_classes = [IsStoreMember]

    def get_queryset(self):
        from inventory.selectors import list_categories
        store = self.get_store()
        search = self.request.query_params.get('search')
        return list_categories(store=store, search=search)


class ItemListCreateAPIView(TenancyMixin, generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsStoreMember]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ItemCreateSerializer
        return ItemSerializer

    def get_queryset(self):
        from inventory.selectors import list_items
        store = self.get_store()
        
        search = self.request.query_params.get('search')
        is_rentable = self.request.query_params.get('is_rentable')
        is_sellable = self.request.query_params.get('is_sellable')
        status = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        
        if is_rentable is not None:
            is_rentable = is_rentable.lower() in ('1', 'true', 'yes')
        if is_sellable is not None:
            is_sellable = is_sellable.lower() in ('1', 'true', 'yes')
        
        return list_items(
            store=store,
            search=search, 
            is_rentable=is_rentable, 
            is_sellable=is_sellable, 
            status=status, 
            category=category
        )


class ItemDetailAPIView(TenancyMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsStoreMember]

    def get_queryset(self):
        store = self.get_store()
        return Item.objects.filter(store=store)

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ItemUpdateSerializer
        return ItemSerializer 