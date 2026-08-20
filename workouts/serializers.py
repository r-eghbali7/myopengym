from rest_framework import serializers

from .models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSet,
    WorkoutSession,
    WorkoutLog,
    WorkoutLogSet,
)


# =========================================================
# Workout Set
# =========================================================

class WorkoutSetSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutSet

        fields = [
            'id',
            'set_number',
            'repetitions',
            'weight',
            'rest_seconds',
            'notes',
        ]

        read_only_fields = [
            'id',
        ]


# =========================================================
# Workout Exercise
# =========================================================

class WorkoutExerciseSerializer(
    serializers.ModelSerializer
):

    exercise_name = serializers.CharField(
        source='exercise.name',
        read_only=True
    )

    sets = WorkoutSetSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = WorkoutExercise

        fields = [
            'id',
            'exercise',
            'exercise_name',
            'order',
            'notes',
            'sets',
        ]

        read_only_fields = [
            'id',
            'exercise_name',
            'sets',
        ]


# =========================================================
# Workout Day
# =========================================================

class WorkoutDaySerializer(
    serializers.ModelSerializer
):

    exercises = WorkoutExerciseSerializer(
        many=True,
        read_only=True
    )

    class Meta:

        model = WorkoutDay

        fields = [
            'id',
            'day_number',
            'name',
            'description',
            'exercises',
        ]

        read_only_fields = [
            'id',
            'exercises',
        ]


# =========================================================
# Workout Plan
# =========================================================

class WorkoutPlanSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutPlan

        fields = [
            'id',
            'name',
            'description',
            'athlete',
            'coach',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'coach',
            'created_at',
        ]

# =========================================================
# Workout Plan Create
# =========================================================

class WorkoutPlanCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutPlan

        fields = [
            'name',
            'description',
            'athlete',
            'start_date',
            'end_date',
            'is_active',
        ]

    def validate_athlete(self, value):

        if value.role != 'athlete':

            raise serializers.ValidationError(
                'Workout plan can only be assigned to an athlete.'
            )

        return value

    def validate(self, attrs):

        start_date = attrs.get(
            'start_date'
        )

        end_date = attrs.get(
            'end_date'
        )

        if (
            start_date
            and end_date
            and end_date < start_date
        ):

            raise serializers.ValidationError(
                'End date cannot be before start date.'
            )

        return attrs


# =========================================================
# Workout Day Create
# =========================================================

class WorkoutDayCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutDay

        fields = [
            'id',
            'day_number',
            'name',
            'description',
        ]

        read_only_fields = [
            'id',
        ]

    def validate_day_number(self, value):

        if value < 1:

            raise serializers.ValidationError(
                'شماره روز باید بزرگ‌تر از صفر باشد.'
            )

        return value


# =========================================================
# Workout Exercise Create
# =========================================================

class WorkoutExerciseCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutExercise

        fields = [
            'id',
            'exercise',
            'order',
            'notes',
        ]

        read_only_fields = [
            'id',
        ]

    def validate_order(self, value):

        if value < 1:

            raise serializers.ValidationError(
                'ترتیب حرکت باید بزرگ‌تر از صفر باشد.'
            )

        return value


# =========================================================
# Workout Set Create
# =========================================================

class WorkoutSetCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutSet

        fields = [
            'id',
            'set_number',
            'repetitions',
            'weight',
            'rest_seconds',
            'notes',
        ]

        read_only_fields = [
            'id',
        ]

    def validate_set_number(self, value):

        if value < 1:

            raise serializers.ValidationError(
                'شماره ست باید بزرگ‌تر از صفر باشد.'
            )

        return value

    def validate_repetitions(self, value):

        if value < 0:

            raise serializers.ValidationError(
                'تعداد تکرار نمی‌تواند منفی باشد.'
            )

        return value

    def validate_weight(self, value):

        if value is not None and value < 0:

            raise serializers.ValidationError(
                'وزنه نمی‌تواند منفی باشد.'
            )

        return value

    def validate_rest_seconds(self, value):

        if value is not None and value < 0:

            raise serializers.ValidationError(
                'زمان استراحت نمی‌تواند منفی باشد.'
            )

        return value


# =========================================================
# Workout Log Set
# =========================================================

class WorkoutLogSetSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutLogSet

        fields = [
            'id',
            'set_number',
            'repetitions',
            'weight',
            'rest_seconds',
            'is_completed',
            'notes',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
        ]

    def validate_set_number(self, value):

        if value < 1:

            raise serializers.ValidationError(
                'شماره ست باید بزرگ‌تر از صفر باشد.'
            )

        return value

    def validate_repetitions(self, value):

        if value <= 0:

            raise serializers.ValidationError(
                'تعداد تکرار باید بیشتر از صفر باشد.'
            )

        return value

    def validate_weight(self, value):

        if value < 0:

            raise serializers.ValidationError(
                'وزنه نمی‌تواند منفی باشد.'
            )

        return value

    def validate_rest_seconds(self, value):

        if value is not None and value < 0:

            raise serializers.ValidationError(
                'زمان استراحت نمی‌تواند منفی باشد.'
            )

        return value


# =========================================================
# Workout Log
# =========================================================

class WorkoutLogSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutLog

        fields = [
            'id',
            'session',
            'workout_exercise',
            'notes',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'session',
            'created_at',
        ]


class WorkoutLogCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutLog

        fields = [
            'workout_exercise',
            'notes',
        ]


# =========================================================
# Workout Session
# =========================================================

class WorkoutSessionSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutSession

        fields = [
            'id',
            'athlete',
            'workout_day',
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
            'created_at',
        ]


class WorkoutSessionCreateSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutSession

        fields = [
            'workout_day',
            'notes',
        ]