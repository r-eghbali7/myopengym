from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    AthleteProfile,
    CoachProfile,
    WeightRecord,
)

from .models import AthleteProfile, CoachProfile
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            'اطلاعات ورزشی',
            {
                'fields': (
                    'role',
                )
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'اطلاعات ورزشی',
            {
                'fields': (
                    'email',
                    'role',
                )
            }
        ),
    )



@admin.register(AthleteProfile)
class AthleteProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'gender',
        'height',
        'goal',
        'activity_level',
    )

    list_filter = (
        'gender',
        'goal',
        'activity_level',
    )


@admin.register(CoachProfile)
class CoachProfileAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'specialization',
        'experience_years',
    )

@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):

    list_display = (
        'athlete',
        'weight',
        'date',
    )

    list_filter = (
        'date',
    )

    search_fields = (
        'athlete__user__username',
    )