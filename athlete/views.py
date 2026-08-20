from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
)

from workouts.models import WorkoutSession

from .serializers import (
    AthleteWorkoutSessionSerializer,
)


class AthleteWorkoutSessionListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = (
        AthleteWorkoutSessionSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_queryset(self):

        return (
            WorkoutSession.objects
            .filter(
                athlete=self.request.user
            )
            .select_related(
                'workout_day',
                'workout_day__workout_plan',
            )
            .order_by(
                '-started_at'
            )
        )

    def perform_create(self, serializer):

        serializer.save(
            athlete=self.request.user
        )


class AthleteWorkoutSessionDetailView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = (
        AthleteWorkoutSessionSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_url_kwarg = 'session_id'

    def get_queryset(self):

        return (
            WorkoutSession.objects
            .filter(
                athlete=self.request.user
            )
            .select_related(
                'workout_day',
                'workout_day__workout_plan',
            )
        )


from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
)

from workouts.models import (
    WorkoutLog,
    WorkoutSession,
)

from .serializers import (
    AthleteWorkoutLogSerializer,
)


class AthleteWorkoutLogListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = (
        AthleteWorkoutLogSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    def get_workout_session(self):

        return get_object_or_404(
            WorkoutSession.objects.select_related(
                'workout_day',
                'workout_day__workout_plan',
            ),
            id=self.kwargs['session_id'],
            athlete=self.request.user
        )

    def get_queryset(self):

        workout_session = (
            self.get_workout_session()
        )

        return (
            WorkoutLog.objects
            .filter(
                session=workout_session
            )
            .select_related(
                'session',
                'workout_exercise',
                'workout_exercise__exercise',
                'workout_exercise__workout_day',
            )
            .order_by('created_at')
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context['workout_session'] = (
            self.get_workout_session()
        )

        return context

    def perform_create(self, serializer):

        workout_session = (
            self.get_workout_session()
        )

        serializer.save(
            session=workout_session
        )


class AthleteWorkoutLogDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = (
        AthleteWorkoutLogSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_url_kwarg = 'log_id'

    def get_queryset(self):

        return (
            WorkoutLog.objects
            .filter(
                session__athlete=self.request.user
            )
            .select_related(
                'session',
                'workout_exercise',
                'workout_exercise__exercise',
                'workout_exercise__workout_day',
                'workout_exercise__workout_day__workout_plan',
            )
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        if self.request.method in [
            'PUT',
            'PATCH'
        ]:

            instance = self.get_object()

            context['workout_session'] = (
                instance.session
            )

        return context