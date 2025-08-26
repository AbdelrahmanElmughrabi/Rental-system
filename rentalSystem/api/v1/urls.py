from django.urls import path
from api.v1.views.auth import WhoAmIView
from api.v1.views.inventory import ItemListCreateAPIView, ItemDetailAPIView
from api.v1.views.rentals import RentalListCreateAPIView, RentalDetailAPIView, RentalReturnAPIView

urlpatterns = [
    path("auth/whoami/", WhoAmIView.as_view()),
    path("items/", ItemListCreateAPIView.as_view()),
    path("items/<int:pk>/", ItemDetailAPIView.as_view()),

    path("rentals/", RentalListCreateAPIView.as_view()),
    path("rentals/<int:pk>/", RentalDetailAPIView.as_view()),
    path("rentals/<int:pk>/return/", RentalReturnAPIView.as_view()),
]
