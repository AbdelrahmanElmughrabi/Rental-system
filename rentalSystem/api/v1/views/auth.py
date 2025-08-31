from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AnonymousUser
from accounts.models import StoreUser


class WhoAmIView(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            # Get user's store memberships
            store_memberships = StoreUser.objects.filter(
                user=user, 
                is_active=True
            ).select_related('store').values(
                'store__id', 
                'store__name', 
                'store__slug', 
                'role'
            )
            
            return Response({
                "id": user.id, 
                "username": user.get_username(),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "store_memberships": list(store_memberships)
            })
        return Response({"anonymous": True})


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {"error": "Username and password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            })
        else:
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"})


class StoreAccessView(APIView):
    """Check if user has access to a specific store."""
    
    def get(self, request, store_id):
        if not request.user.is_authenticated:
            return Response({"has_access": False}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            store_user = StoreUser.objects.get(
                user=request.user,
                store_id=store_id,
                is_active=True
            )
            return Response({
                "has_access": True,
                "role": store_user.role,
                "store": {
                    "id": store_user.store.id,
                    "name": store_user.store.name,
                    "slug": store_user.store.slug
                }
            })
        except StoreUser.DoesNotExist:
            return Response({"has_access": False}, status=status.HTTP_403_FORBIDDEN)
