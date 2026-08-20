from rest_framework.permissions import BasePermission


class IsCoach(BasePermission):

    message = 'فقط مربی می‌تواند به این بخش دسترسی داشته باشد.'

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'coach'
        )