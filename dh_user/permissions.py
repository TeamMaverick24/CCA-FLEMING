from rest_framework.permissions import BasePermission


class IsUserProfileOwner(BasePermission):
    """
    Check if authenticated user is owner of the profile
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsUserAddressOwner(BasePermission):
    """
    Check if authenticated user is owner of the address
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated is True

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class IsActiveStudent(BasePermission):
    """
    Check if authenticated Student is Active
    """

    def has_permission(self, request, view):
        try:
            permission_key = request.user.is_deleted is False
        except:
            permission_key = False
            
        return permission_key

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_deleted is False
