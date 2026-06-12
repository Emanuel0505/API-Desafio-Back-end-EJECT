from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLojista(BasePermission):
    """
    Permissão customizada para Lojista
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.usertype == 'L' or request.user.is_staff)
        )
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        
        
        return bool(
            request.user.is_staff or 
            (hasattr(obj, 'author') and obj.author == request.user)
        ) 

class IsCliente(BasePermission):
    """
    Permissão customizada para clientes
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.usertype == 'C' or request.user.is_staff)
        )

