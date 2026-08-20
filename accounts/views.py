from decimal import Decimal

from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AthleteProfile,
    CoachProfile,
    WeightRecord,
)

from .serializers import (
    CoachAthleteSerializer,
    RegisterSerializer,
    UserSerializer,
    AthleteProfileSerializer,
    WeightRecordSerializer,
    ProgressSerializer,
)

from django.db.models import (
    Count,
    Sum,
    F,
    DecimalField,
    ExpressionWrapper,
)

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSession,
    WorkoutLogSet,
)



# =========================================================
# Register
# =========================================================

class RegisterView(
    generics.CreateAPIView
):

    serializer_class = RegisterSerializer

    permission_classes = [
        AllowAny
    ]


# =========================================================
# Current User
# =========================================================

class MeView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        serializer = UserSerializer(
            request.user
        )

        return Response(
            serializer.data
        )


# =========================================================
# Athlete Profile
# =========================================================

class AthleteProfileView(
    generics.RetrieveUpdateAPIView
):

    serializer_class = AthleteProfileSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_object(self):

        return get_object_or_404(
            AthleteProfile,
            user=self.request.user
        )


# =========================================================
# Weight Records
# =========================================================

class WeightRecordListCreateView(
    generics.ListCreateAPIView
):

    serializer_class = WeightRecordSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return (
            WeightRecord.objects
            .filter(
                athlete__user=self.request.user
            )
            .order_by('-date')
        )

    def perform_create(self, serializer):

        # فقط ورزشکار می‌تواند وزن ثبت کند
        if self.request.user.role != 'athlete':

            raise PermissionDenied(
                'Only athletes can add weight records.'
            )

        athlete = get_object_or_404(
            AthleteProfile,
            user=self.request.user
        )

        serializer.save(
            athlete=athlete
        )


class ProgressView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        # =================================================
        # Athlete
        # =================================================

        athlete = get_object_or_404(
            AthleteProfile,
            user=request.user
        )

        # =================================================
        # Weight Progress
        # =================================================

        weight_records = list(
            WeightRecord.objects
            .filter(
                athlete=athlete
            )
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

            bmi = athlete.calculate_bmi(
                current_weight
            )

            bmi_status = athlete.bmi_status(
                current_weight
            )

        else:

            starting_weight = None
            current_weight = None
            weight_change = None
            bmi = None
            bmi_status = None

        # =================================================
        # Workout Plans
        # =================================================

        workout_plans = WorkoutPlan.objects.filter(
            athlete=request.user
        )

        total_plans = workout_plans.count()

        # =================================================
        # Workout Days
        # =================================================

        total_days = WorkoutDay.objects.filter(
            workout_plan__in=workout_plans
        ).count()

        # =================================================
        # Workout Exercises
        # =================================================

        total_exercises = WorkoutExercise.objects.filter(
            workout_day__workout_plan__in=workout_plans
        ).count()

        # =================================================
        # Workout Sessions
        # =================================================

        workout_sessions = WorkoutSession.objects.filter(
            athlete=request.user
        )

        total_sessions = workout_sessions.count()

        completed_sessions = workout_sessions.filter(
            is_completed=True
        ).count()

        # =================================================
        # Workout Volume
        # =================================================
        #
        # Volume =
        # repetitions × weight
        #
        # Example:
        #
        # 10 reps × 60kg = 600kg
        #
        # =================================================

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
                workout_log__session__athlete=request.user
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

        # =================================================
        # Weight History
        # =================================================

        history = []

        for record in weight_records:

            history.append({
                'id': record.id,
                'weight': record.weight,
                'date': record.date,
                'note': record.note,
                'created_at': record.created_at,
            })

        # =================================================
        # Response Data
        # =================================================

        data = {

            'weight': {

                'current': current_weight,

                'starting': starting_weight,

                'change': weight_change,

                'bmi': bmi,

                'bmi_status': bmi_status,

                'history': history,
            },

            'workouts': {

                'total_plans': total_plans,

                'total_days': total_days,

                'total_exercises': total_exercises,

                'total_sessions': total_sessions,

                'completed_sessions': (
                    completed_sessions
                ),

                'total_volume': total_volume,
            }
        }

        # =================================================
        # Serializer
        # =================================================

        serializer = ProgressSerializer(
            data
        )

        return Response(
            serializer.data
        )


class CoachAthletesView(APIView):

    permission_classes = [
        IsAuthenticated
    ]


    def get(self, request):

        if request.user.role != 'coach':

            raise PermissionDenied(
                "Only coaches can access athletes."
            )


        coach = get_object_or_404(
            CoachProfile,
            user=request.user
        )


        athletes = AthleteProfile.objects.filter(
            coaches__coach=coach
        )


        serializer = CoachAthleteSerializer(
            athletes,
            many=True
        )


        return Response(
            serializer.data
        )