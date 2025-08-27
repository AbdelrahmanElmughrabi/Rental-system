from rest_framework import serializers

from rentals.models import Rental, RentalItem, ReturnReport


class RentalItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_sku = serializers.CharField(source='item.sku', read_only=True)

    class Meta:
        model = RentalItem
        fields = ['id', 'item', 'item_name', 'item_sku', 'qty', 'per_day', 'returned_qty']


class ReturnReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnReport
        fields = ['id', 'rental_item', 'returned_at', 'notes', 'damage_cost']
        read_only_fields = ['returned_at']


class RentalSerializer(serializers.ModelSerializer):
    items = RentalItemSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source='store.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Rental
        fields = [
            'id', 'store', 'store_name', 'created_by', 'created_by_username', 'customer_name', 
            'start_date', 'due_date', 'returned_date', 'status', 'total', 'items'
        ]
        read_only_fields = ['id', 'start_date', 'status', 'items']


class RentalCreateSerializer(serializers.ModelSerializer):
    items = RentalItemSerializer(many=True)

    class Meta:
        model = Rental
        fields = ['store', 'customer_name', 'due_date', 'items']

    def create(self, validated_data):
        from rentals.services import RentalService
        items_data = validated_data.pop('items')
        return RentalService.create_rental(
            store=validated_data['store'],
            created_by=self.context['request'].user,
            customer_name=validated_data['customer_name'],
            due_date=validated_data['due_date'],
            items=items_data,
        )


class RentalReturnSerializer(serializers.Serializer):
    returned_items = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of items being returned with quantities and notes"
    )

    def save(self, **kwargs):
        from rentals.services import RentalService
        rental_id = self.context['rental_id']
        return RentalService.process_return(
            rental_id=rental_id, 
            returned_items=self.validated_data['returned_items']
        ) 