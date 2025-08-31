from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from stores.models import Store


class ServiceResult:
    def __init__(self, success: bool, data=None, error: str | None = None):
        self.success = success
        self.data = data
        self.error = error

    @classmethod
    def ok(cls, data=None):
        return cls(True, data=data)

    @classmethod
    def fail(cls, error: str):
        return cls(False, error=error)


class TenancyMixin:
    """
    Mixin to enforce store-scoped data access.
    Ensures users can only access data from stores they belong to.
    """
    
    def get_store(self):
        """Get store from URL parameters or request context."""
        store_id = self.kwargs.get('store')
        if store_id:
            return get_object_or_404(Store, id=store_id)
        return None
    
    def get_queryset(self):
        """Filter queryset by store if store-scoped."""
        queryset = super().get_queryset()
        store = self.get_store()
        
        if store and hasattr(queryset.model, 'store'):
            return queryset.filter(store=store)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set store on creation if not already set."""
        store = self.get_store()
        if store and not serializer.validated_data.get('store'):
            serializer.save(store=store)
        else:
            serializer.save()


class IsStoreMember(permissions.BasePermission):
    """
    Permission class to check if user is a member of the store.
    """
    
    def has_permission(self, request, view):
        # Allow if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if user is member of the store
        store = view.get_store()
        if not store:
            return False
        
        return store.members.filter(user=request.user, is_active=True).exists()


class IsStoreAdmin(permissions.BasePermission):
    """
    Permission class to check if user is an admin of the store.
    """
    
    def has_permission(self, request, view):
        # Allow if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Check if user is admin of the store
        store = view.get_store()
        if not store:
            return False
        
        return store.members.filter(
            user=request.user, 
            is_active=True,
            role__in=['owner', 'admin']
        ).exists()
