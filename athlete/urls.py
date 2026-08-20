from django.urls import path

from .views import (
    AthleteWorkoutSessionListCreateView,
    AthleteWorkoutSessionDetailView,
    AthleteWorkoutLogListCreateView,
    AthleteWorkoutLogDetailView,
)


urlpatterns = [

    # =====================================================
    # Workout Sessions
    # =====================================================

    path(
        'workout-sessions/',
        AthleteWorkoutSessionListCreateView.as_view(),
        name='athlete-workout-session-list-create'
    ),

    path(
        'workout-sessions/<int:session_id>/',
        AthleteWorkoutSessionDetailView.as_view(),
        name='athlete-workout-session-detail'
    ),

    # =====================================================
    # Workout Logs
    # =====================================================

    path(
        'workout-sessions/<int:session_id>/logs/',
        AthleteWorkoutLogListCreateView.as_view(),
        name='athlete-workout-log-list-create'
    ),

    path(
        'workout-logs/<int:log_id>/',
        AthleteWorkoutLogDetailView.as_view(),
        name='athlete-workout-log-detail'
    ),
]