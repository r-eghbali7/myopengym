from rest_framework.permissions import BasePermission


class IsAthlete(BasePermission):

    message = 'فقط ورزشکار می‌تواند این عملیات را انجام دهد.'

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == 'athlete'
        )


class IsCoach(BasePermission):
    """
    فقط مربی اجازه دارد
    """

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role == 'coach'
        )


class IsAthleteOrCoach(BasePermission):

    message = 'فقط ورزشکار یا مربی مجاز است.'

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role in [
                'athlete',
                'coach',
            ]
        )


class IsCoachOwnWorkout(BasePermission):
    """
    فقط صاحب برنامه (Coach) اجازه دارد
    """

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):

        return (
            obj.coach == request.user
        )