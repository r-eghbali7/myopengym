from rest_framework.permissions import BasePermission


class IsAthlete(BasePermission):

    message = 'فقط ورزشکاران به این بخش دسترسی دارند.'

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == 'athlete'
        )


class IsCoach(BasePermission):

    message = 'فقط مربیان به این بخش دسترسی دارند.'

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == 'coach'
        )


class IsAthleteOrCoach(BasePermission):

    message = 'فقط ورزشکار یا مربی می‌تواند دسترسی داشته باشد.'

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role in [
                'athlete',
                'coach',
            ]
        )