from django.contrib import admin

from .models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSet,
)


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'athlete',
        'coach',
        'start_date',
        'end_date',
        'is_active',
    )

    list_filter = (
        'is_active',
        'start_date',
        'end_date',
    )

    search_fields = (
        'name',
        'athlete__username',
        'coach__username',
    )


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):

    list_display = (
        'workout_plan',
        'day_number',
        'name',
    )

    list_filter = (
        'day_number',
    )


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):

    list_display = (
        'workout_day',
        'exercise',
        'order',
    )


@admin.register(WorkoutSet)
class WorkoutSetAdmin(admin.ModelAdmin):

    list_display = (
        'workout_exercise',
        'set_number',
        'repetitions',
        'weight',
        'rest_seconds',
    )