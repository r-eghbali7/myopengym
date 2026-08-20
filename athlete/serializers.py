from django.utils import timezone

from rest_framework import serializers

from workouts.models import (
    WorkoutSession,
)


class AthleteWorkoutSessionSerializer(
    serializers.ModelSerializer
):

    workout_day_name = serializers.CharField(
        source='workout_day.name',
        read_only=True
    )

    workout_plan_name = serializers.CharField(
        source='workout_day.workout_plan.name',
        read_only=True
    )

    class Meta:

        model = WorkoutSession

        fields = [
            'id',
            'athlete',
            'workout_day',
            'workout_day_name',
            'workout_plan_name',
            'started_at',
            'finished_at',
            'notes',
            'is_completed',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'athlete',
            'started_at',
            'finished_at',
            'created_at',
        ]

    def validate_workout_day(
        self,
        workout_day
    ):

        request = self.context.get(
            'request'
        )

        if request is None:
            return workout_day

        athlete = request.user

        if (
            workout_day.workout_plan.athlete_id
            != athlete.id
        ):

            raise serializers.ValidationError(
                'این روز تمرینی متعلق به شما نیست.'
            )

        return workout_day

    def validate(self, attrs):

        is_completed = attrs.get(
            'is_completed'
        )

        if (
            self.instance is not None
            and self.instance.is_completed
            and is_completed is False
        ):

            raise serializers.ValidationError(
                {
                    'is_completed': (
                        'یک Session تکمیل‌شده '
                        'نمی‌تواند دوباره فعال شود.'
                    )
                }
            )

        return attrs

    def update(
        self,
        instance,
        validated_data
    ):

        is_completed = validated_data.get(
            'is_completed'
        )

        if (
            is_completed is True
            and not instance.is_completed
        ):

            instance.finished_at = timezone.now()

        instance = super().update(
            instance,
            validated_data
        )

        return instance


from rest_framework import serializers

from workouts.models import (
    WorkoutLog,
    WorkoutSession,
)


class AthleteWorkoutLogSerializer(
    serializers.ModelSerializer
):

    exercise_name = serializers.CharField(
        source='workout_exercise.exercise.name',
        read_only=True
    )

    session_id = serializers.IntegerField(
        source='session.id',
        read_only=True
    )

    class Meta:

        model = WorkoutLog

        fields = [
            'id',
            'session',
            'session_id',
            'workout_exercise',
            'exercise_name',
            'notes',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'session',
            'session_id',
            'exercise_name',
            'created_at',
        ]

    def validate_workout_exercise(
        self,
        workout_exercise
    ):

        request = self.context.get(
            'request'
        )

        if request is None:
            return workout_exercise

        athlete = request.user

        workout_day = (
            workout_exercise.workout_day
        )

        workout_plan = (
            workout_day.workout_plan
        )

        if workout_plan.athlete_id != athlete.id:

            raise serializers.ValidationError(
                'این حرکت متعلق به برنامه تمرینی شما نیست.'
            )

        return workout_exercise

    def validate(self, attrs):

        request = self.context.get(
            'request'
        )

        if request is None:
            return attrs

        athlete = request.user

        # ==========================================
        # جلوگیری از تغییر Session
        # ==========================================

        if (
            self.instance is not None
            and 'session' in self.initial_data
        ):

            raise serializers.ValidationError(
                {
                    'session': (
                        'امکان تغییر Session وجود ندارد.'
                    )
                }
            )

        workout_exercise = attrs.get(
            'workout_exercise'
        )

        if workout_exercise is None:
            return attrs

        session = self.context.get(
            'workout_session'
        )

        if session is not None:

            if session.athlete_id != athlete.id:

                raise serializers.ValidationError(
                    {
                        'session': (
                            'این Session متعلق به شما نیست.'
                        )
                    }
                )

            if (
                session.workout_day_id
                != workout_exercise.workout_day_id
            ):

                raise serializers.ValidationError(
                    {
                        'workout_exercise': (
                            'این حرکت متعلق به '
                            'روز تمرینی Session نیست.'
                        )
                    }
                )

            queryset = WorkoutLog.objects.filter(
                session=session,
                workout_exercise=workout_exercise
            )

            if self.instance is not None:

                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():

                raise serializers.ValidationError(
                    {
                        'workout_exercise': (
                            'این حرکت قبلاً در '
                            'این Session ثبت شده است.'
                        )
                    }
                )

        return attrs


        