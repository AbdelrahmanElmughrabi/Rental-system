from django.urls import path
from api.v1.views.auth import WhoAmIView

urlpatterns = [
    path("auth/whoami/", WhoAmIView.as_view()),
]
