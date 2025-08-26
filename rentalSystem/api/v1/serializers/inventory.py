from rest_framework import serializers

from inventory.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = [
            'id', 'name', 'sku', 'description', 'price', 'quantity', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'sku', 'description', 'price', 'quantity', 'is_active']

    def create(self, validated_data):
        from inventory.services import InventoryService
        return InventoryService.create_item(**validated_data)


class ItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'quantity', 'is_active']

    def update(self, instance, validated_data):
        from inventory.services import InventoryService
        return InventoryService.update_item(item=instance, **validated_data) 