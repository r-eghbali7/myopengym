from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.db.models import (
    F,
    Sum,
    DecimalField,
    ExpressionWrapper,
)

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import (
    AthleteProfile,
    CoachProfile,
)

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSession,
    WorkoutLogSet,
    WorkoutSet,
)

from .permissions import IsCoach

from .serializers import (
    CoachAthleteListSerializer,
    CoachAthleteDetailSerializer,
    CoachAthleteProgressSerializer,
    CoachProfileSerializer,
    CoachWorkoutPlanSerializer,
    CoachWorkoutDaySerializer,
    CoachWorkoutExerciseSerializer,
    CoachWorkoutSetSerializer,
)


# =========================================================
# Helper
# =========================================================

def get_coach_athlete_ids(user):

    return (
        WorkoutPlan.objects
        .filter(
            coach=user
        )
        .values_list(
            'athlete_id',
            flat=True
        )
        .distinct()
    )


# =========================================================
# Athlete List
# =========================================================

class CoachAthleteListView(
    generics.ListAPIView
):

    serializer_class = (
        CoachAthleteListSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    def get_queryset(self):

        athlete_ids = get_coach_athlete_ids(
            self.request.user
        )

        return (
            AthleteProfile.objects
            .filter(
                user_id__in=athlete_ids
            )
            .select_related('user')
            .prefetch_related('weight_records')
        )


# =========================================================
# Athlete Detail
# =========================================================

class CoachAthleteDetailView(
    generics.RetrieveAPIView
):

    serializer_class = (
        CoachAthleteDetailSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    lookup_url_kwarg = 'athlete_id'

    def get_queryset(self):

        athlete_ids = get_coach_athlete_ids(
            self.request.user
        )

        return (
            AthleteProfile.objects
            .filter(
                user_id__in=athlete_ids
            )
            .select_related('user')
            .prefetch_related('weight_records')
        )

    def get_object(self):

        athlete_id = self.kwargs[
            self.lookup_url_kwarg
        ]

        queryset = self.get_queryset()

        return get_object_or_404(
            queryset,
            user_id=athlete_id
        )


# =========================================================
# Athlete Progress
# =========================================================

class CoachAthleteProgressView(
    generics.GenericAPIView
):

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    serializer_class = (
        CoachAthleteProgressSerializer
    )

    def get(self, request, athlete_id):

        athlete_profile = get_object_or_404(
            AthleteProfile.objects
            .select_related('user')
            .prefetch_related('weight_records'),
            user_id=athlete_id
        )

        # -------------------------------------------------
        # Security
        # -------------------------------------------------

        if not WorkoutPlan.objects.filter(
            coach=request.user,
            athlete=athlete_profile.user
        ).exists():

            return Response(
                {
                    'detail': (
                        'You do not have access '
                        'to this athlete.'
                    )
                },
                status=403
            )

        # -------------------------------------------------
        # Weight
        # -------------------------------------------------

        weight_records = list(
            athlete_profile
            .weight_records
            .order_by('date')
        )

        if weight_records:

            starting_weight = (
                weight_records[0].weight
            )

            current_weight = (
                weight_records[-1].weight
            )

            weight_change = (
                current_weight -
                starting_weight
            )

            bmi = athlete_profile.calculate_bmi(
                current_weight
            )

            bmi_status = athlete_profile.bmi_status(
                current_weight
            )

        else:

            starting_weight = None
            current_weight = None
            weight_change = None
            bmi = None
            bmi_status = None

        # -------------------------------------------------
        # Plans
        # -------------------------------------------------

        plans = WorkoutPlan.objects.filter(
            coach=request.user,
            athlete=athlete_profile.user
        )

        total_plans = plans.count()

        active_plans = plans.filter(
            is_active=True
        ).count()

        # -------------------------------------------------
        # Days
        # -------------------------------------------------

        total_days = WorkoutDay.objects.filter(
            workout_plan__in=plans
        ).count()

        # -------------------------------------------------
        # Exercises
        # -------------------------------------------------

        total_exercises = (
            WorkoutExercise.objects
            .filter(
                workout_day__workout_plan__in=plans
            )
            .count()
        )

        # -------------------------------------------------
        # Sessions
        # -------------------------------------------------

        sessions = WorkoutSession.objects.filter(
            athlete=athlete_profile.user,
            workout_day__workout_plan__in=plans
        )

        total_sessions = sessions.count()

        completed_sessions = (
            sessions
            .filter(is_completed=True)
            .count()
        )

        if total_sessions:

            completion_rate = round(
                (
                    completed_sessions /
                    total_sessions
                ) * 100,
                2
            )

        else:

            completion_rate = 0

        # -------------------------------------------------
        # Volume
        # -------------------------------------------------

        volume_expression = ExpressionWrapper(
            F('repetitions') * F('weight'),
            output_field=DecimalField(
                max_digits=12,
                decimal_places=2
            )
        )

        volume_result = (
            WorkoutLogSet.objects
            .filter(
                workout_log__session__athlete=athlete_profile.user,
                workout_log__session__workout_day__workout_plan__in=plans
            )
            .aggregate(
                total=Sum(
                    volume_expression
                )
            )
        )

        total_volume = (
            volume_result['total']
            or Decimal('0.00')
        )

        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        data = {

            'total_plans': total_plans,

            'active_plans': active_plans,

            'total_days': total_days,

            'total_exercises': total_exercises,

            'total_sessions': total_sessions,

            'completed_sessions': (
                completed_sessions
            ),

            'completion_rate': (
                completion_rate
            ),

            'total_volume': (
                total_volume
            ),

            'current_weight': (
                current_weight
            ),

            'starting_weight': (
                starting_weight
            ),

            'weight_change': (
                weight_change
            ),

            'bmi': bmi,

            'bmi_status': bmi_status,
        }

        serializer = (
            self.get_serializer(data)
        )

        return Response(
            serializer.data
        )


# =========================================================
# Athlete Workout Plans
# =========================================================

class CoachAthleteWorkoutListView(
    generics.ListAPIView
):

    serializer_class = (
        CoachWorkoutPlanSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    def get_queryset(self):

        athlete_id = self.kwargs[
            'athlete_id'
        ]

        return (
            WorkoutPlan.objects
            .filter(
                coach=self.request.user,
                athlete_id=athlete_id
            )
            .order_by('-created_at')
        )


# =========================================================
# Coach Profile
# =========================================================

class CoachProfileView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = CoachProfileSerializer

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    def get_object(self):

        return get_object_or_404(
            CoachProfile.objects
            .select_related('user'),
            user=self.request.user
        )


# =========================================================
# Coach Workout Plan List / Create
# =========================================================

class CoachWorkoutPlanListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = CoachWorkoutPlanSerializer

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    def get_queryset(self):

        return (
            WorkoutPlan.objects
            .filter(
                coach=self.request.user
            )
            .select_related(
                'athlete',
                'coach',
            )
            .order_by('-created_at')
        )

    def perform_create(self, serializer):

        athlete = serializer.validated_data.get(
            'athlete'
        )

        # ---------------------------------------------
        # Athlete باید به این Coach اختصاص داده شده باشد
        # ---------------------------------------------

        assigned = WorkoutPlan.objects.filter(
            coach=self.request.user,
            athlete=athlete
        ).exists()

        if not assigned:

            from rest_framework.exceptions import (
                PermissionDenied
            )

            raise PermissionDenied(
                'این ورزشکار به شما اختصاص داده نشده است.'
            )

        serializer.save(
            coach=self.request.user
        )


# =========================================================
# Coach Workout Plan Detail
# =========================================================

class CoachWorkoutPlanDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = CoachWorkoutPlanSerializer

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    lookup_url_kwarg = 'plan_id'

    def get_queryset(self):

        return (
            WorkoutPlan.objects
            .filter(
                coach=self.request.user
            )
            .select_related(
                'athlete',
                'coach',
            )
        )


# =========================================================
# Coach Workout Day List / Create
# =========================================================

class CoachWorkoutDayListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = (
        CoachWorkoutDaySerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    def get_workout_plan(self):

        return get_object_or_404(
            WorkoutPlan,
            id=self.kwargs['plan_id'],
            coach=self.request.user
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context['workout_plan'] = (
            self.get_workout_plan()
        )

        return context

    def get_queryset(self):

        workout_plan = self.get_workout_plan()

        return (
            WorkoutDay.objects
            .filter(
                workout_plan=workout_plan
            )
            .prefetch_related(
                'exercises'
            )
            .order_by(
                'day_number'
            )
        )

    def perform_create(self, serializer):

        workout_plan = self.get_workout_plan()

        day_number = serializer.validated_data.get(
            'day_number'
        )

        # =====================================================
        # Duplicate Day Number
        # =====================================================

        if WorkoutDay.objects.filter(
            workout_plan=workout_plan,
            day_number=day_number
        ).exists():

            from rest_framework.exceptions import (
                ValidationError
            )

            raise ValidationError(
                {
                    'day_number': (
                        'A workout day with this '
                        'day number already exists '
                        'for this workout plan.'
                    )
                }
            )

        serializer.save(
            workout_plan=workout_plan
        )


# =========================================================
# Coach Workout Day Detail
# =========================================================

class CoachWorkoutDayDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = (
        CoachWorkoutDaySerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    lookup_url_kwarg = 'day_id'

    def get_queryset(self):

        return (
            WorkoutDay.objects
            .filter(
                workout_plan__coach=self.request.user
            )
            .select_related(
                'workout_plan'
            )
            .prefetch_related(
                'exercises'
            )
        )


# =========================================================
# Coach Workout Exercise List / Create
# =========================================================

class CoachWorkoutExerciseListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = (
        CoachWorkoutExerciseSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    def get_workout_day(self):

        return get_object_or_404(
            WorkoutDay.objects.select_related(
                'workout_plan'
            ),
            id=self.kwargs['day_id'],
            workout_plan__coach=self.request.user
        )

    def get_queryset(self):

        workout_day = self.get_workout_day()

        return (
            WorkoutExercise.objects
            .filter(
                workout_day=workout_day
            )
            .select_related(
                'exercise',
                'workout_day',
            )
            .order_by('order')
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context['workout_day'] = (
            self.get_workout_day()
        )

        return context

    def perform_create(self, serializer):

        workout_day = self.get_workout_day()

        order = serializer.validated_data.get(
            'order'
        )

        if WorkoutExercise.objects.filter(
            workout_day=workout_day,
            order=order
        ).exists():

            from rest_framework.exceptions import (
                ValidationError
            )

            raise ValidationError(
                {
                    'order': (
                        'An exercise with this '
                        'order already exists '
                        'for this workout day.'
                    )
                }
            )

        serializer.save(
            workout_day=workout_day
        )


# =========================================================
# Coach Workout Exercise Detail
# =========================================================

class CoachWorkoutExerciseDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = (
        CoachWorkoutExerciseSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    lookup_url_kwarg = 'exercise_id'

    def get_queryset(self):

        return (
            WorkoutExercise.objects
            .filter(
                workout_day__workout_plan__coach=(
                    self.request.user
                )
            )
            .select_related(
                'exercise',
                'workout_day',
                'workout_day__workout_plan',
            )
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        if self.request.method in [
            'PUT',
            'PATCH'
        ]:

            instance = self.get_object()

            context['workout_day'] = (
                instance.workout_day
            )

        return context


# =========================================================
# Coach Workout Set List / Create
# =========================================================

class CoachWorkoutSetListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = (
        CoachWorkoutSetSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    def get_workout_exercise(self):

        return get_object_or_404(
            WorkoutExercise.objects.select_related(
                'workout_day',
                'workout_day__workout_plan',
                'exercise',
            ),
            id=self.kwargs['exercise_id'],
            workout_day__workout_plan__coach=(
                self.request.user
            )
        )

    def get_queryset(self):

        workout_exercise = (
            self.get_workout_exercise()
        )

        return (
            WorkoutSet.objects
            .filter(
                workout_exercise=workout_exercise
            )
            .order_by('set_number')
        )

    def get_serializer_context(self):

        context = super().get_serializer_context()

        context['workout_exercise'] = (
            self.get_workout_exercise()
        )

        return context

    def perform_create(self, serializer):

        workout_exercise = (
            self.get_workout_exercise()
        )

        serializer.save(
            workout_exercise=workout_exercise
        )


# =========================================================
# Coach Workout Set Detail
# =========================================================

class CoachWorkoutSetDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = (
        CoachWorkoutSetSerializer
    )

    permission_classes = [
        IsAuthenticated,
        IsCoach,
    ]

    lookup_url_kwarg = 'set_id'

    def get_queryset(self):

        return (
            WorkoutSet.objects
            .filter(
                workout_exercise__workout_day__workout_plan__coach=(
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

    def get_serializer_context(self):

        context = super().get_serializer_context()

        if self.request.method in [
            'PUT',
            'PATCH'
        ]:

            instance = self.get_object()

            context['workout_exercise'] = (
                instance.workout_exercise
            )

        return context

