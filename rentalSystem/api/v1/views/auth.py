from rest_framework.views import APIView
from rest_framework.response import Response

class WhoAmIView(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            return Response({"id": user.id, "username": user.get_username()})
        return Response({"anonymous": True})
