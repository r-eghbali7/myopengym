from rest_framework import serializers

from accounts.models import (
    AthleteProfile,
    CoachProfile,
)

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSession,
    WorkoutSet,
)


# =========================================================
# Athlete List
# =========================================================

class CoachAthleteListSerializer(
    serializers.ModelSerializer
):

    current_weight = serializers.SerializerMethodField()

    goal = serializers.SerializerMethodField()

    class Meta:

        model = AthleteProfile

        fields = [
            'id',
            'current_weight',
            'goal',
        ]

    def get_current_weight(self, obj):

        record = (
            obj.weight_records
            .order_by('-date')
            .first()
        )

        if not record:
            return None

        return str(record.weight)

    def get_goal(self, obj):

        return obj.goal


# =========================================================
# Athlete Detail
# =========================================================

class CoachAthleteDetailSerializer(
    serializers.ModelSerializer
):

    user = serializers.SerializerMethodField()

    current_weight = serializers.SerializerMethodField()

    starting_weight = serializers.SerializerMethodField()

    weight_change = serializers.SerializerMethodField()

    bmi = serializers.SerializerMethodField()

    bmi_status = serializers.SerializerMethodField()

    class Meta:

        model = AthleteProfile

        fields = [
            'id',
            'user',
            'gender',
            'birth_date',
            'height',
            'goal',
            'activity_level',
            'current_weight',
            'starting_weight',
            'weight_change',
            'bmi',
            'bmi_status',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'user',
            'current_weight',
            'starting_weight',
            'weight_change',
            'bmi',
            'bmi_status',
            'created_at',
            'updated_at',
        ]

    # =====================================================
    # User
    # =====================================================

    def get_user(self, obj):

        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }

    # =====================================================
    # Current Weight
    # =====================================================

    def get_current_weight(self, obj):

        record = (
            obj.weight_records
            .order_by('-date')
            .first()
        )

        if not record:
            return None

        return str(record.weight)

    # =====================================================
    # Starting Weight
    # =====================================================

    def get_starting_weight(self, obj):

        record = (
            obj.weight_records
            .order_by('date')
            .first()
        )

        if not record:
            return None

        return str(record.weight)

    # =====================================================
    # Weight Change
    # =====================================================

    def get_weight_change(self, obj):

        records = list(
            obj.weight_records
            .order_by('date')
        )

        if len(records) < 2:
            return '0.00'

        change = (
            records[-1].weight -
            records[0].weight
        )

        return f'{change:.2f}'

    # =====================================================
    # BMI
    # =====================================================

    def get_bmi(self, obj):

        weight = self.get_current_weight(obj)

        if weight is None:
            return None

        return obj.calculate_bmi(
            weight
        )

    # =====================================================
    # BMI Status
    # =====================================================

    def get_bmi_status(self, obj):

        weight = self.get_current_weight(obj)

        if weight is None:
            return None

        return obj.bmi_status(
            weight
        )


# =========================================================
# Workout Plan
# =========================================================

class CoachWorkoutPlanSerializer(
    serializers.ModelSerializer
):

    total_days = serializers.SerializerMethodField()

    total_exercises = serializers.SerializerMethodField()

    total_sessions = serializers.SerializerMethodField()

    completed_sessions = serializers.SerializerMethodField()

    class Meta:

        model = WorkoutPlan

        fields = [
            'id',
            'name',
            'description',

            # Assignment
            'athlete',
            'coach',

            # Dates
            'start_date',
            'end_date',

            # Status
            'is_active',

            # Statistics
            'total_days',
            'total_exercises',
            'total_sessions',
            'completed_sessions',

            # Timestamps
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'coach',

            'total_days',
            'total_exercises',
            'total_sessions',
            'completed_sessions',

            'created_at',
            'updated_at',
        ]

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, attrs):

        start_date = attrs.get(
            'start_date'
        )

        end_date = attrs.get(
            'end_date'
        )

        # در PATCH ممکن است یکی از این‌ها
        # ارسال نشده باشد.
        if (
            start_date is not None
            and end_date is not None
            and end_date < start_date
        ):

            raise serializers.ValidationError({
                'end_date':
                    'تاریخ پایان نمی‌تواند '
                    'قبل از تاریخ شروع باشد.'
            })

        return attrs

    # =====================================================
    # Total Days
    # =====================================================

    def get_total_days(self, obj):

        return WorkoutDay.objects.filter(
            workout_plan=obj
        ).count()

    # =====================================================
    # Total Exercises
    # =====================================================

    def get_total_exercises(self, obj):

        return WorkoutExercise.objects.filter(
            workout_day__workout_plan=obj
        ).count()

    # =====================================================
    # Total Sessions
    # =====================================================

    def get_total_sessions(self, obj):

        return WorkoutSession.objects.filter(
            workout_day__workout_plan=obj
        ).count()

    # =====================================================
    # Completed Sessions
    # =====================================================

    def get_completed_sessions(self, obj):

        return WorkoutSession.objects.filter(
            workout_day__workout_plan=obj,
            is_completed=True
        ).count()


# =========================================================
# Athlete Progress
# =========================================================

class CoachAthleteProgressSerializer(
    serializers.Serializer
):

    total_plans = serializers.IntegerField()

    active_plans = serializers.IntegerField()

    total_days = serializers.IntegerField()

    total_exercises = serializers.IntegerField()

    total_sessions = serializers.IntegerField()

    completed_sessions = serializers.IntegerField()

    completion_rate = serializers.FloatField()

    total_volume = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    current_weight = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True
    )

    starting_weight = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True
    )

    weight_change = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        allow_null=True
    )

    bmi = serializers.FloatField(
        allow_null=True
    )

    bmi_status = serializers.CharField(
        allow_null=True
    )


# =========================================================
# Coach Profile
# =========================================================

class CoachProfileSerializer(
    serializers.ModelSerializer
):

    user = serializers.SerializerMethodField()

    class Meta:

        model = CoachProfile

        fields = [
            'id',
            'user',
            'bio',
            'specialization',
            'experience_years',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
        ]

    # =====================================================
    # User
    # =====================================================

    def get_user(self, obj):

        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }

    # =====================================================
    # Experience
    # =====================================================

    def validate_experience_years(self, value):

        if value < 0:

            raise serializers.ValidationError(
                'سابقه نمی‌تواند منفی باشد.'
            )

        if value > 100:

            raise serializers.ValidationError(
                'مقدار سابقه وارد شده غیرمنطقی است.'
            )

        return value



# =========================================================
# Coach Workout Day
# =========================================================

class CoachWorkoutDaySerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WorkoutDay

        fields = [
            'id',
            'workout_plan',
            'day_number',
            'name',
            'description',
        ]

        read_only_fields = [
            'id',
            'workout_plan',
        ]

    # =====================================================
    # Validate Day Number
    # =====================================================

    def validate_day_number(self, value):

        if value < 1:
            raise serializers.ValidationError(
                'Day number must be greater than 0.'
            )

        return value

    # =====================================================
    # Validate Duplicate Day Number
    # =====================================================

    def validate(self, attrs):

        workout_plan = attrs.get(
            'workout_plan'
        )

        day_number = attrs.get(
            'day_number'
        )

        # در زمان ایجاد، workout_plan هنوز داخل
        # validated_data نیست چون View آن را با
        # serializer.save(workout_plan=...) اضافه می‌کند.
        #
        # بنابراین plan را از context می‌گیریم.

        if workout_plan is None:

            workout_plan = self.context.get(
                'workout_plan'
            )

        if (
            workout_plan is not None
            and day_number is not None
        ):

            queryset = WorkoutDay.objects.filter(
                workout_plan=workout_plan,
                day_number=day_number
            )

            # اگر در حال UPDATE هستیم،
            # خود رکورد فعلی را کنار می‌گذاریم.

            if self.instance is not None:

                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():

                raise serializers.ValidationError(
                    {
                        'day_number': (
                            'A workout day with this '
                            'day number already exists '
                            'for this workout plan.'
                        )
                    }
                )

        return attrs


# =========================================================
# Coach Workout Exercise
# =========================================================

class CoachWorkoutExerciseSerializer(
    serializers.ModelSerializer
):

    exercise_name = serializers.CharField(
        source='exercise.name',
        read_only=True
    )

    order = serializers.IntegerField(
        required=True,
        min_value=1
    )

    class Meta:

        model = WorkoutExercise

        fields = [
            'id',
            'workout_day',
            'exercise',
            'exercise_name',
            'order',
            'notes',
        ]

        read_only_fields = [
            'id',
            'workout_day',
            'exercise_name',
        ]

# =========================================================
# Coach Workout Set
# =========================================================

class CoachWorkoutSetSerializer(
    serializers.ModelSerializer
):

    exercise_name = serializers.CharField(
        source='workout_exercise.exercise.name',
        read_only=True
    )

    class Meta:

        model = WorkoutSet

        fields = [
            'id',
            'workout_exercise',
            'exercise_name',
            'set_number',
            'repetitions',
            'weight',
            'rest_seconds',
            'notes',
        ]

        read_only_fields = [
            'id',
            'workout_exercise',
            'exercise_name',
        ]

    # =====================================================
    # Set Number
    # =====================================================

    def validate_set_number(self, value):

        if value < 1:

            raise serializers.ValidationError(
                'Set number must be greater than 0.'
            )

        return value

    # =====================================================
    # Repetitions
    # =====================================================

    def validate_repetitions(self, value):

        if value is not None and value < 1:

            raise serializers.ValidationError(
                'Repetitions must be greater than 0.'
            )

        return value

    # =====================================================
    # Weight
    # =====================================================

    def validate_weight(self, value):

        if value is not None and value < 0:

            raise serializers.ValidationError(
                'Weight cannot be negative.'
            )

        return value

    # =====================================================
    # Rest
    # =====================================================

    def validate_rest_seconds(self, value):

        if value is not None and value < 0:

            raise serializers.ValidationError(
                'Rest seconds cannot be negative.'
            )

        return value

    # =====================================================
    # Duplicate Set Number
    # =====================================================

    def validate(self, attrs):

        workout_exercise = attrs.get(
            'workout_exercise'
        )

        set_number = attrs.get(
            'set_number'
        )

        if workout_exercise is None:

            workout_exercise = self.context.get(
                'workout_exercise'
            )

        if (
            workout_exercise is not None
            and set_number is not None
        ):

            queryset = WorkoutSet.objects.filter(
                workout_exercise=workout_exercise,
                set_number=set_number
            )

            # هنگام UPDATE رکورد خودش را حذف می‌کنیم

            if self.instance is not None:

                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():

                raise serializers.ValidationError(
                    {
                        'set_number': (
                            'A set with this '
                            'set number already exists '
                            'for this exercise.'
                        )
                    }
                )

        return attrs

    



