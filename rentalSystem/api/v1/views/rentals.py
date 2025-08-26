from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import DefaultPagination
from rentals.models import Rental
from ..serializers.rentals import (
    RentalSerializer,
    RentalCreateSerializer,
    RentalReturnSerializer,
)


class RentalListCreateAPIView(generics.ListCreateAPIView):
    queryset = Rental.objects.all().order_by('-rented_at')
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RentalCreateSerializer
        return RentalSerializer

    def get_queryset(self):
        from rentals.selectors import list_rentals
        params = self.request.query_params
        return list_rentals(
            status=params.get('status'),
            item_id=params.get('item_id'),
            date_from=params.get('date_from'),
            date_to=params.get('date_to'),
        )


class RentalDetailAPIView(generics.RetrieveAPIView):
    queryset = Rental.objects.all().select_related('item')
    serializer_class = RentalSerializer


class RentalReturnAPIView(APIView):
    def post(self, request, pk: int):
        serializer = RentalReturnSerializer(data=request.data, context={'rental_id': pk})
        serializer.is_valid(raise_exception=True)
        rental = serializer.save()
        return Response(RentalSerializer(rental).data, status=status.HTTP_200_OK) 