from rest_framework import permissions

class IsAuthenticatedAndInAdminGroup(permissions.BasePermission):
    """
    Allows access only to authenticated users who are in the ADMIN group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        # Check if the user is in the ADMIN group
        return request.user.role in ['admin']
    
class IsAuthenticatedAndInAdminorExecutiveGroup(permissions.BasePermission):
    """
    Allows access only to authenticated users who are in the ADMIN group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        # Check if the user is in the ADMIN group
        return request.user.role in ['admin','executive']

class IsAuthenticatedAndInExecutiveGroup(permissions.BasePermission):
    """
    Allows access only to authenticated users who are in the Executive group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        # Check if the user is in the ADMIN group
        return request.user.role in ['executive']
    
class IsAuthenticatedAndInAgentGroup(permissions.BasePermission):
    """
    Allows access only to authenticated users who are in the Executive group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        # Check if the user is in the ADMIN group
        return request.user.role in ['agent']
    
class IsAuthenticatedAndInSuperAdminAGroup(permissions.BasePermission):
    """
    Allows access only to authenticated users who are in the Executive group.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        # Check if the user is in the ADMIN group
        return request.user.role in ['superadmin']