from django.conf import settings
from django.db import models

from exercises.models import Exercise


class WorkoutPlan(models.Model):

    name = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workout_plans'
    )

    coach = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_workout_plans'
    )

    start_date = models.DateField(
        null=True,
        blank=True
    )

    end_date = models.DateField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            '-created_at'
        ]

    def __str__(self):

        return self.name


class WorkoutDay(models.Model):

    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name='days'
    )

    day_number = models.PositiveIntegerField()

    name = models.CharField(
        max_length=255,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f'{self.workout_plan.name} - '
            f'Day {self.day_number}'
        )

    class Meta:
        ordering = ['day_number']

        unique_together = (
            'workout_plan',
            'day_number',
        )


class WorkoutExercise(models.Model):

    workout_day = models.ForeignKey(
        WorkoutDay,
        on_delete=models.CASCADE,
        related_name='exercises'
    )

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.PROTECT,
        related_name='workout_exercises'
    )

    order = models.PositiveIntegerField(
        default=1
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f'{self.workout_day} - '
            f'{self.exercise.name}'
        )

    class Meta:
        ordering = ['order']


class WorkoutSet(models.Model):

    workout_exercise = models.ForeignKey(
        WorkoutExercise,
        on_delete=models.CASCADE,
        related_name='sets'
    )

    set_number = models.PositiveIntegerField()

    repetitions = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    rest_seconds = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f'{self.workout_exercise.exercise.name} '
            f'- Set {self.set_number}'
        )

    class Meta:
        ordering = ['set_number']

        unique_together = (
            'workout_exercise',
            'set_number',
        )

class WorkoutSession(models.Model):

    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workout_sessions'
    )

    workout_day = models.ForeignKey(
        WorkoutDay,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    started_at = models.DateTimeField(
        auto_now_add=True
    )

    finished_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    is_completed = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = [
            '-started_at'
        ]

    def __str__(self):

        return (
            f"{self.athlete} - "
            f"{self.workout_day.name} - "
            f"{self.started_at}"
        )
    

class WorkoutLog(models.Model):

    session = models.ForeignKey(
        WorkoutSession,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    workout_exercise = models.ForeignKey(
        WorkoutExercise,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.session} - "
            f"{self.workout_exercise.exercise.name}"
        )

class WorkoutLogSet(models.Model):

    workout_log = models.ForeignKey(
        WorkoutLog,
        on_delete=models.CASCADE,
        related_name='sets'
    )

    set_number = models.PositiveIntegerField()

    repetitions = models.PositiveIntegerField()

    weight = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0
    )

    rest_seconds = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    is_completed = models.BooleanField(
        default=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"Set {self.set_number} - "
            f"{self.repetitions} reps - "
            f"{self.weight} kg"
        )