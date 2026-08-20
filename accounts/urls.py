from django.urls import path

from .views import (
    CoachAthletesView,
    RegisterView,
    MeView,
    AthleteProfileView,
    WeightRecordListCreateView,
    ProgressView,
)


urlpatterns = [

    path(
        'register/',
        RegisterView.as_view(),
        name='register'
    ),

    path(
        'me/',
        MeView.as_view(),
        name='me'
    ),

    path(
        'profile/',
        AthleteProfileView.as_view(),
        name='athlete-profile'
    ),

    path(
        'weights/',
        WeightRecordListCreateView.as_view(),
        name='weight-list-create'
    ),

    path(
        'progress/',
        ProgressView.as_view(),
        name='progress'
    ),

    path(
        'coach/athletes/',
        CoachAthletesView.as_view(),
        name='coach-athletes'
    ),
]