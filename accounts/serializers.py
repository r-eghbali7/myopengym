from datetime import date

from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import (
    AthleteProfile,
    WeightRecord,
)


User = get_user_model()


# =========================================================
# Register
# =========================================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:

        model = User

        fields = [
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'role',
        ]

    def validate_email(self, value):

        if User.objects.filter(
            email__iexact=value
        ).exists():

            raise serializers.ValidationError(
                'این ایمیل قبلاً ثبت شده است.'
            )

        return value

    def validate_role(self, value):

        allowed_roles = [
            User.Role.ATHLETE,
            User.Role.COACH,
        ]

        if value not in allowed_roles:

            raise serializers.ValidationError(
                'نقش کاربر نامعتبر است.'
            )

        return value

    def create(self, validated_data):

        password = validated_data.pop(
            'password'
        )

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user


# =========================================================
# User
# =========================================================

class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
        ]

        read_only_fields = [
            'id',
            'username',
            'role',
        ]


# =========================================================
# Weight Record
# =========================================================

class WeightRecordSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = WeightRecord

        fields = [
            'id',
            'weight',
            'date',
            'note',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
        ]

    # -----------------------------------------------------
    # Validate Weight
    # -----------------------------------------------------

    def validate_weight(self, value):

        if value <= 0:

            raise serializers.ValidationError(
                'وزن باید بیشتر از صفر باشد.'
            )

        if value > 500:

            raise serializers.ValidationError(
                'وزن وارد شده غیرمنطقی است.'
            )

        return value

    # -----------------------------------------------------
    # Validate Date
    # -----------------------------------------------------

    def validate_date(self, value):

        if value > date.today():

            raise serializers.ValidationError(
                'تاریخ وزن نمی‌تواند در آینده باشد.'
            )

        return value


# =========================================================
# Athlete Profile
# =========================================================

class AthleteProfileSerializer(
    serializers.ModelSerializer
):

    current_weight = serializers.SerializerMethodField()

    bmi = serializers.SerializerMethodField()

    bmi_status = serializers.SerializerMethodField()

    class Meta:

        model = AthleteProfile

        fields = [
            'id',
            'gender',
            'birth_date',
            'height',
            'goal',
            'activity_level',
            'current_weight',
            'bmi',
            'bmi_status',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'current_weight',
            'bmi',
            'bmi_status',
            'created_at',
            'updated_at',
        ]

    # -----------------------------------------------------
    # Current Weight
    # -----------------------------------------------------

    def get_current_weight(self, obj):

        record = (
            obj.weight_records
            .order_by('-date')
            .first()
        )

        if not record:

            return None

        return record.weight

    # -----------------------------------------------------
    # BMI
    # -----------------------------------------------------

    def get_bmi(self, obj):

        weight = self.get_current_weight(obj)

        if weight is None:

            return None

        return obj.calculate_bmi(
            weight
        )

    # -----------------------------------------------------
    # BMI Status
    # -----------------------------------------------------

    def get_bmi_status(self, obj):

        weight = self.get_current_weight(obj)

        if weight is None:

            return None

        return obj.bmi_status(
            weight
        )


# =========================================================
# Weight Progress
# =========================================================

class WeightProgressSerializer(
    serializers.Serializer
):

    current = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True
    )

    starting = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        allow_null=True
    )

    change = serializers.DecimalField(
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

    history = WeightRecordSerializer(
        many=True
    )


# =========================================================
# Workout Progress
# =========================================================

class WorkoutProgressSerializer(
    serializers.Serializer
):

    total_plans = serializers.IntegerField()

    total_days = serializers.IntegerField()

    total_exercises = serializers.IntegerField()

    total_sessions = serializers.IntegerField()

    completed_sessions = serializers.IntegerField()

    total_volume = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )


# =========================================================
# Overall Progress
# =========================================================

class ProgressSerializer(
    serializers.Serializer
):

    weight = WeightProgressSerializer()

    workouts = WorkoutProgressSerializer()



class CoachAthleteSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField(
        source='user.username'
    )

    email = serializers.EmailField(
        source='user.email'
    )


    class Meta:

        model = AthleteProfile

        fields = [
            'id',
            'username',
            'email',
            'height',
            'goal',
            'activity_level',
        ]