from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsShopkeeper(BasePermission):
    """Allow shopkeepers and staff to mutate commerce resources.

    Safe methods are always allowed. Write operations require an authenticated
    user with ``usertype == 'L'`` or staff status. Object access is limited to
    staff or the owner shopkeeper when the object exposes a ``shopkeeper``
    attribute.
    """

    def has_permission(self, request, view):
        """Check whether the request can reach a shopkeeper-protected endpoint."""
        if request.method in SAFE_METHODS:
            return True
        
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.usertype == 'L' or request.user.is_staff)
        )
    def has_object_permission(self, request, view, obj):
        """Check whether the requester can act on a specific object instance."""
        if request.method in SAFE_METHODS:
            return True
        
        
        return bool(
            request.user.is_staff or 
            (hasattr(obj, 'shopkeeper') and obj.shopkeeper == request.user)
        ) 

class IsCustomer(BasePermission):
    """Allow customers and staff to access customer-owned resources.

    Safe methods are always allowed. Write operations require an authenticated
    user with ``usertype == 'C'`` or staff status. Object access is limited to
    staff or the owner user/cart depending on the target object.
    """
    def has_permission(self, request, view):
        """Check whether the request can reach a customer-protected endpoint."""
        if request.method in SAFE_METHODS:
            return True
        
        return bool(
            request.user and
            request.user.is_authenticated and
            (getattr(request.user, 'usertype', None) == 'C' or request.user.is_staff)
        )
    def has_object_permission(self, request, view, obj):
        """Check whether the requester can act on the specific customer object."""
        if request.method in SAFE_METHODS:
            return True
        
        if hasattr(obj, 'cart'):
            return bool(
                request.user.is_staff or obj.cart.user == request.user
            )
        
        return bool(
            request.user.is_staff or 
            (hasattr(obj, 'user') and obj.user == request.user)
        )

