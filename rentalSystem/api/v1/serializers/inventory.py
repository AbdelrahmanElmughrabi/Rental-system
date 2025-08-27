from rest_framework import serializers

from inventory.models import Item, Category, InventoryTransaction


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class InventoryTransactionSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = ['id', 'item', 'delta', 'reason', 'actor', 'actor_username', 'created_at']
        read_only_fields = ['id', 'created_at']


class ItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    store_name = serializers.CharField(source='store.name', read_only=True)

    class Meta:
        model = Item
        fields = [
            'id', 'store', 'store_name', 'category', 'category_id', 'name', 'sku', 'description', 
            'is_rentable', 'is_sellable', 'price', 'rental_rate', 'quantity', 'status', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ItemCreateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Item
        fields = [
            'store', 'category_id', 'name', 'sku', 'description', 'is_rentable', 'is_sellable', 
            'price', 'rental_rate', 'quantity', 'status'
        ]

    def create(self, validated_data):
        from inventory.services import InventoryService
        category_id = validated_data.pop('category_id', None)
        category = None
        if category_id:
            category = Category.objects.filter(
                store=validated_data['store'], 
                id=category_id
            ).first()
        
        return InventoryService.create_item(
            category=category,
            **validated_data
        )


class ItemUpdateSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Item
        fields = [
            'category_id', 'name', 'description', 'is_rentable', 'is_sellable', 
            'price', 'rental_rate', 'status'
        ]

    def update(self, instance, validated_data):
        from inventory.services import InventoryService
        category_id = validated_data.pop('category_id', None)
        if category_id is not None:
            category = None
            if category_id:
                category = Category.objects.filter(
                    store=instance.store, 
                    id=category_id
                ).first()
            instance.category = category
        
        return InventoryService.update_item(item=instance, **validated_data) 