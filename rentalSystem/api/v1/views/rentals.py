from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import DefaultPagination
from core.mixins import TenancyMixin, IsStoreMember
from rentals.models import Rental
from ..serializers.rentals import (
    RentalSerializer,
    RentalCreateSerializer,
    RentalReturnSerializer,
)


class RentalListCreateAPIView(TenancyMixin, generics.ListCreateAPIView):
    queryset = Rental.objects.all().order_by('-start_date')
    pagination_class = DefaultPagination
    permission_classes = [IsStoreMember]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RentalCreateSerializer
        return RentalSerializer

    def get_queryset(self):
        from rentals.selectors import list_rentals
        params = self.request.query_params
        store = self.get_store()
        return list_rentals(
            store=store,
            status=params.get('status'),
            item_id=params.get('item_id'),
            date_from=params.get('date_from'),
            date_to=params.get('date_to'),
        )


class RentalDetailAPIView(TenancyMixin, generics.RetrieveAPIView):
    queryset = Rental.objects.all().select_related('store')
    serializer_class = RentalSerializer
    permission_classes = [IsStoreMember]


class RentalReturnAPIView(TenancyMixin, APIView):
    permission_classes = [IsStoreMember]
    
    def post(self, request, pk: int):
        serializer = RentalReturnSerializer(data=request.data, context={'rental_id': pk})
        serializer.is_valid(raise_exception=True)
        rental = serializer.save()
        return Response(RentalSerializer(rental).data, status=status.HTTP_200_OK) 