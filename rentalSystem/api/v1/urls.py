from django.urls import path
from api.v1.views.auth import WhoAmIView, LoginView, LogoutView, StoreAccessView
from api.v1.views.inventory import (
    CategoryListAPIView, ItemListCreateAPIView, ItemDetailAPIView
)
from api.v1.views.rentals import (
    RentalListCreateAPIView, RentalDetailAPIView, RentalReturnAPIView
)

urlpatterns = [
    # Authentication endpoints
    path("auth/whoami/", WhoAmIView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/store-access/<int:store_id>/", StoreAccessView.as_view()),
    
    # Store-scoped inventory endpoints
    path("stores/<int:store>/categories/", CategoryListAPIView.as_view()),
    path("stores/<int:store>/items/", ItemListCreateAPIView.as_view()),
    path("stores/<int:store>/items/<int:pk>/", ItemDetailAPIView.as_view()),

    # Store-scoped rental endpoints
    path("stores/<int:store>/rentals/", RentalListCreateAPIView.as_view()),
    path("stores/<int:store>/rentals/<int:pk>/", RentalDetailAPIView.as_view()),
    path("stores/<int:store>/rentals/<int:pk>/return/", RentalReturnAPIView.as_view()),
]
