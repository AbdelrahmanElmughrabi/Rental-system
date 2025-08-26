from rest_framework import serializers

from rentals.models import Rental


class RentalSerializer(serializers.ModelSerializer):
    item_sku = serializers.CharField(source='item.sku', read_only=True)

    class Meta:
        model = Rental
        fields = [
            'id', 'item', 'item_sku', 'customer_name', 'rented_at', 'due_date', 'returned_at', 'status'
        ]
        read_only_fields = ['id', 'rented_at', 'returned_at', 'status']


class RentalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = ['item', 'customer_name', 'due_date']

    def create(self, validated_data):
        from rentals.services import RentalService
        return RentalService.create_rental(
            item_id=validated_data['item'].id,
            customer_name=validated_data['customer_name'],
            due_date=validated_data['due_date'],
        )


class RentalReturnSerializer(serializers.Serializer):
    returned_at = serializers.DateTimeField(required=False)

    def save(self, **kwargs):
        from rentals.services import RentalService
        rental_id = self.context['rental_id']
        return RentalService.return_rental(rental_id=rental_id, returned_at=self.validated_data.get('returned_at')) 