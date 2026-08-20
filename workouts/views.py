from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, serializers

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from accounts.models import AthleteProfile, CoachAthleteRelation

from .models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSet,
    WorkoutSession,
    WorkoutLog,
    WorkoutLogSet,
)

from .serializers import (
    WorkoutPlanSerializer,
    WorkoutPlanCreateSerializer,

    WorkoutDaySerializer,
    WorkoutDayCreateSerializer,

    WorkoutExerciseSerializer,
    WorkoutExerciseCreateSerializer,

    WorkoutSetSerializer,
    WorkoutSetCreateSerializer,

    WorkoutSessionSerializer,
    WorkoutSessionCreateSerializer,

    WorkoutLogSerializer,
    WorkoutLogCreateSerializer,

    WorkoutLogSetSerializer,
)

from .permissions import (
    IsAthlete,
    IsCoach,
)


# =========================================================
# Workout Plan
# =========================================================

class WorkoutPlanListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = WorkoutPlanSerializer


    permission_classes = [
        IsAuthenticated
    ]


    def get_queryset(self):

        user = self.request.user


        if user.role == 'coach':

            return WorkoutPlan.objects.filter(
                coach=user
            )


        elif user.role == 'athlete':

            return WorkoutPlan.objects.filter(
                athlete=user
            )


        return WorkoutPlan.objects.none()



    def perform_create(
        self,
        serializer
    ):

        user = self.request.user


        # فقط Coach

        if user.role != 'coach':

            raise PermissionDenied(
                "Only coaches can create workout plans."
            )


        athlete_id = self.request.data.get(
            'athlete'
        )


        if not athlete_id:

            raise PermissionDenied(
                "Athlete is required."
            )


        athlete = get_object_or_404(
            AthleteProfile,
            id=athlete_id
        )


        relation = (
            CoachAthleteRelation.objects
            .filter(
                coach__user=user,
                athlete=athlete
            )
            .exists()
        )


        if not relation:

            raise PermissionDenied(
                "This athlete is not assigned to you."
            )


        serializer.save(
            coach=user,
            athlete=athlete.user
        )

# =========================================================
# Workout Plan Detail
# =========================================================

class WorkoutPlanDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = WorkoutPlanSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        user = self.request.user


        if user.role == 'coach':

            return WorkoutPlan.objects.filter(
                coach=user
            )


        return WorkoutPlan.objects.filter(
            athlete=user
        )

# =========================================================
# Workout Day
# =========================================================

class WorkoutDayListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = WorkoutDayCreateSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return (
            WorkoutDay.objects
            .filter(
                workout_plan__athlete=self.request.user
            )
            .select_related(
                'workout_plan'
            )
            .prefetch_related(
                'exercises__exercise',
                'exercises__sets',
            )
        )

    def perform_create(self, serializer):

        workout_plan = get_object_or_404(
            WorkoutPlan,
            id=self.kwargs['workout_id'],
            athlete=self.request.user
        )

        serializer.save(
            workout_plan=workout_plan
        )


# =========================================================
# Workout Day Detail
# =========================================================

class WorkoutDayDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def get_serializer_class(self):

        if self.request.method in [
            'PUT',
            'PATCH',
        ]:

            return WorkoutDayCreateSerializer

        return WorkoutDaySerializer

    def get_queryset(self):

        return (
            WorkoutDay.objects
            .filter(
                workout_plan__athlete=self.request.user
            )
            .select_related(
                'workout_plan'
            )
            .prefetch_related(
                'exercises__exercise',
                'exercises__sets',
            )
        )

    def update(self, request, *args, **kwargs):

        if request.user.role != 'coach':

            raise PermissionDenied(
                'Only coaches can update workout days.'
            )

        return super().update(
            request,
            *args,
            **kwargs
        )

    def destroy(self, request, *args, **kwargs):

        if request.user.role != 'coach':

            raise PermissionDenied(
                'Only coaches can delete workout days.'
            )

        return super().destroy(
            request,
            *args,
            **kwargs
        )


# =========================================================
# Workout Exercise
# =========================================================

class WorkoutExerciseListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = WorkoutExerciseCreateSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return (
            WorkoutExercise.objects
            .filter(
                workout_day__workout_plan__athlete=self.request.user
            )
            .select_related(
                'exercise',
                'workout_day',
                'workout_day__workout_plan',
            )
            .prefetch_related(
                'sets'
            )
        )

    def perform_create(self, serializer):

        workout_day = get_object_or_404(
            WorkoutDay,
            id=self.kwargs['day_id'],
            workout_plan__athlete=self.request.user
        )

        serializer.save(
            workout_day=workout_day
        )


# =========================================================
# Workout Exercise Detail
# =========================================================

class WorkoutExerciseDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def get_serializer_class(self):

        if self.request.method in [
            'PUT',
            'PATCH',
        ]:

            return WorkoutExerciseCreateSerializer

        return WorkoutExerciseSerializer

    def get_queryset(self):

        return (
            WorkoutExercise.objects
            .filter(
                workout_day__workout_plan__athlete=(
                    self.request.user
                )
            )
            .select_related(
                'exercise',
                'workout_day',
                'workout_day__workout_plan',
            )
            .prefetch_related(
                'sets'
            )
        )

    def update(self, request, *args, **kwargs):

        if request.user.role != 'coach':

            raise PermissionDenied(
                'Only coaches can update exercises.'
            )

        return super().update(
            request,
            *args,
            **kwargs
        )

    def destroy(self, request, *args, **kwargs):

        if request.user.role != 'coach':

            raise PermissionDenied(
                'Only coaches can delete exercises.'
            )

        return super().destroy(
            request,
            *args,
            **kwargs
        )


# =========================================================
# Workout Set
# =========================================================

class WorkoutSetListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = WorkoutSetCreateSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return (
            WorkoutSet.objects
            .filter(
                workout_exercise__workout_day__workout_plan__athlete=self.request.user
            )
            .select_related(
                'workout_exercise',
                'workout_exercise__exercise',
                'workout_exercise__workout_day',
                'workout_exercise__workout_day__workout_plan',
            )
        )

    def perform_create(self, serializer):

        workout_exercise = get_object_or_404(
            WorkoutExercise,
            id=self.kwargs['exercise_id'],
            workout_day__workout_plan__athlete=self.request.user
        )

        serializer.save(
            workout_exercise=workout_exercise
        )


# =========================================================
# Workout Set Detail
# =========================================================

class WorkoutSetDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def get_serializer_class(self):

        return WorkoutSetCreateSerializer

    def get_queryset(self):

        return (
            WorkoutSet.objects
            .filter(
                workout_exercise__workout_day__workout_plan__athlete=(
                    self.request.user
                )
            )
            .select_related(
                'workout_exercise',
                'workout_exercise__exercise',
                'workout_exercise__workout_day',
                'workout_exercise__workout_day__workout_plan',
            )
        )

    def update(self, request, *args, **kwargs):

        if request.user.role != 'coach':

            raise PermissionDenied(
                'Only coaches can update sets.'
            )

        return super().update(
            request,
            *args,
            **kwargs
        )

    def destroy(self, request, *args, **kwargs):

        if request.user.role != 'coach':

            raise PermissionDenied(
                'Only coaches can delete sets.'
            )

        return super().destroy(
            request,
            *args,
            **kwargs
        )


# =========================================================
# Workout Session
# =========================================================

class WorkoutSessionListCreateView(
    generics.ListCreateAPIView
):

    permission_classes = [
        IsAthlete
    ]

    def get_serializer_class(self):

        if self.request.method == 'POST':

            return WorkoutSessionCreateSerializer

        return WorkoutSessionSerializer

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
            .prefetch_related(
                'logs__workout_exercise__exercise',
                'logs__sets',
            )
            .order_by(
                '-started_at'
            )
        )

    def perform_create(self, serializer):

        workout_day = serializer.validated_data[
            'workout_day'
        ]

        if workout_day.workout_plan.athlete != self.request.user:

            raise PermissionDenied(
                'You can only start your own workouts.'
            )

        serializer.save(
            athlete=self.request.user
        )


# =========================================================
# Workout Session Detail
# =========================================================

class WorkoutSessionDetailView(
    generics.RetrieveUpdateAPIView
):

    permission_classes = [
        IsAthlete
    ]

    serializer_class = WorkoutSessionSerializer

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
            .prefetch_related(
                'logs__workout_exercise__exercise',
                'logs__sets',
            )
        )

    def update(self, request, *args, **kwargs):

        session = self.get_object()

        if session.is_completed:

            raise PermissionDenied(
                'Cannot modify a completed workout.'
            )

        return super().update(
            request,
            *args,
            **kwargs
        )


# =========================================================
# Start Session
# =========================================================

class WorkoutSessionStartView(
    generics.CreateAPIView
):

    serializer_class = WorkoutSessionSerializer

    permission_classes = [
        IsAthlete
    ]

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        workout_day = get_object_or_404(
            WorkoutDay,
            id=kwargs['day_id'],
            workout_plan__athlete=request.user
        )

        existing_session = (
            WorkoutSession.objects
            .filter(
                athlete=request.user,
                workout_day=workout_day,
                is_completed=False
            )
            .first()
        )

        if existing_session:

            serializer = self.get_serializer(
                existing_session
            )

            return Response(
                serializer.data,
                status=200
            )

        session = WorkoutSession.objects.create(
            athlete=request.user,
            workout_day=workout_day
        )

        serializer = self.get_serializer(
            session
        )

        return Response(
            serializer.data,
            status=201
        )


# =========================================================
# Finish Session
# =========================================================

class WorkoutSessionFinishView(
    generics.GenericAPIView
):

    serializer_class = WorkoutSessionSerializer

    permission_classes = [
        IsAthlete
    ]

    def post(
        self,
        request,
        *args,
        **kwargs
    ):

        session = get_object_or_404(
            WorkoutSession,
            id=kwargs['pk'],
            athlete=request.user
        )

        if session.is_completed:

            serializer = self.get_serializer(
                session
            )

            return Response(
                serializer.data,
                status=200
            )

        session.finished_at = timezone.now()

        session.is_completed = True

        session.save(
            update_fields=[
                'finished_at',
                'is_completed',
            ]
        )

        serializer = self.get_serializer(
            session
        )

        return Response(
            serializer.data,
            status=200
        )


# =========================================================
# Workout Log
# =========================================================

class WorkoutLogListCreateView(
    generics.ListCreateAPIView
):

    permission_classes = [
        IsAthlete
    ]

    def get_serializer_class(self):

        if self.request.method == 'POST':

            return WorkoutLogCreateSerializer

        return WorkoutLogSerializer

    def get_queryset(self):

        return (
            WorkoutLog.objects
            .filter(
                session__id=self.kwargs['session_id'],
                session__athlete=self.request.user
            )
            .select_related(
                'workout_exercise',
                'workout_exercise__exercise',
            )
            .prefetch_related(
                'sets'
            )
        )

    def perform_create(self, serializer):

        session = get_object_or_404(
            WorkoutSession,
            id=self.kwargs['session_id'],
            athlete=self.request.user
        )

        if session.is_completed:

            raise PermissionDenied(
                'Cannot add logs to a completed workout.'
            )

        workout_exercise = get_object_or_404(
            WorkoutExercise,
            id=serializer.validated_data[
                'workout_exercise'
            ].id,
            workout_day=session.workout_day
        )

        serializer.save(
            session=session,
            workout_exercise=workout_exercise
        )


# =========================================================
# Workout Log Set
# =========================================================

class WorkoutLogSetListCreateView(
    generics.ListCreateAPIView
):

    permission_classes = [
        IsAthlete
    ]

    serializer_class = WorkoutLogSetSerializer

    def get_queryset(self):

        return (
            WorkoutLogSet.objects
            .filter(
                workout_log__id=self.kwargs['log_id'],
                workout_log__session__athlete=self.request.user
            )
            .select_related(
                'workout_log',
                'workout_log__session',
            )
            .order_by(
                'set_number'
            )
        )

    def perform_create(self, serializer):

        workout_log = get_object_or_404(
            WorkoutLog,
            id=self.kwargs['log_id'],
            session__athlete=self.request.user
        )

        if workout_log.session.is_completed:

            raise PermissionDenied(
                'Cannot add sets to a completed workout.'
            )

        serializer.save(
            workout_log=workout_log
        )


