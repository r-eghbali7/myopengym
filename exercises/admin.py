from django.contrib import admin

from .models import Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'body_part',
        'equipment',
        'target_muscle',
        'difficulty',
        'is_active',
    )

    list_filter = (
        'category',
        'body_part',
        'equipment',
        'difficulty',
        'is_active',
    )

    search_fields = (
        'name',
        'target_muscle',
        'muscle_group',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }