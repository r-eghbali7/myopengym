from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        ATHLETE = 'athlete', 'ورزشکار'
        COACH = 'coach', 'مربی'

    email = models.EmailField(
        unique=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ATHLETE
    )

    def __str__(self):
        return self.username


from django.conf import settings
from django.db import models


class AthleteProfile(models.Model):

    class Gender(models.TextChoices):
        MALE = 'male', 'مرد'
        FEMALE = 'female', 'زن'

    class Goal(models.TextChoices):
        WEIGHT_LOSS = 'weight_loss', 'کاهش وزن'
        MUSCLE_GAIN = 'muscle_gain', 'افزایش حجم'
        FAT_LOSS = 'fat_loss', 'چربی سوزی'
        MAINTENANCE = 'maintenance', 'حفظ وزن'

    class ActivityLevel(models.TextChoices):
        SEDENTARY = 'sedentary', 'کم تحرک'
        LIGHT = 'light', 'فعالیت سبک'
        MODERATE = 'moderate', 'فعالیت متوسط'
        HIGH = 'high', 'فعالیت زیاد'
        VERY_HIGH = 'very_high', 'فعالیت بسیار زیاد'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='athlete_profile'
    )

    gender = models.CharField(
        max_length=10,
        choices=Gender.choices
    )

    birth_date = models.DateField(
        null=True,
        blank=True
    )

    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Height in centimeters'
    )

    goal = models.CharField(
        max_length=20,
        choices=Goal.choices
    )

    activity_level = models.CharField(
        max_length=20,
        choices=ActivityLevel.choices
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f'{self.user.username} - Athlete'

    def calculate_bmi(self, weight):

        if not self.height:
            return None

        height_in_meters = (
            float(self.height) / 100
        )

        if height_in_meters <= 0:
            return None

        return round(
            float(weight) /
            (height_in_meters ** 2),
            2
        )

    def bmi_status(self, weight):

        bmi = self.calculate_bmi(weight)

        if bmi is None:
            return None

        if bmi < 18.5:
            return 'underweight'

        if bmi < 25:
            return 'normal'

        if bmi < 30:
            return 'overweight'

        return 'obese'

class CoachProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coach_profile'
    )

    bio = models.TextField(
        blank=True
    )

    specialization = models.CharField(
        max_length=255,
        blank=True
    )

    experience_years = models.PositiveIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f'{self.user.username} - Coach'


class WeightRecord(models.Model):

    athlete = models.ForeignKey(
        AthleteProfile,
        on_delete=models.CASCADE,
        related_name='weight_records'
    )

    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    date = models.DateField()

    note = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ['-date']

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'athlete',
                    'date',
                ],
                name='unique_athlete_weight_date'
            )
        ]

    def __str__(self):
        return f'{self.athlete.user.username} - {self.weight} kg - {self.date}'


class CoachAthleteRelation(models.Model):

    coach = models.ForeignKey(
        CoachProfile,
        on_delete=models.CASCADE,
        related_name='athletes'
    )

    athlete = models.ForeignKey(
        AthleteProfile,
        on_delete=models.CASCADE,
        related_name='coaches'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


    class Meta:

        unique_together = (
            'coach',
            'athlete',
        )


    def __str__(self):

        return (
            f'{self.coach.user.username} '
            f'-> '
            f'{self.athlete.user.username}'
        )