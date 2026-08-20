from django.urls import path

from .views import (
    WorkoutPlanListCreateView,
    WorkoutPlanDetailView,

    WorkoutDayListCreateView,
    WorkoutDayDetailView,

    WorkoutExerciseListCreateView,
    WorkoutExerciseDetailView,

    WorkoutSetListCreateView,
    WorkoutSetDetailView,

    WorkoutSessionListCreateView,
    WorkoutSessionDetailView,

    WorkoutSessionStartView,
    WorkoutSessionFinishView,

    WorkoutLogListCreateView,
    WorkoutLogSetListCreateView,
)


urlpatterns = [

    # =====================================================
    # Workout Plans
    # =====================================================

    path(
        '',
        WorkoutPlanListCreateView.as_view(),
        name='workout-list-create'
    ),

    path(
        '<int:pk>/',
        WorkoutPlanDetailView.as_view(),
        name='workout-detail'
    ),

    # =====================================================
    # Workout Days
    # =====================================================

    path(
        '<int:workout_id>/days/',
        WorkoutDayListCreateView.as_view(),
        name='workout-day-list-create'
    ),

    path(
        'days/<int:pk>/',
        WorkoutDayDetailView.as_view(),
        name='workout-day-detail'
    ),

    # =====================================================
    # Workout Exercises
    # =====================================================

    path(
        'days/<int:day_id>/exercises/',
        WorkoutExerciseListCreateView.as_view(),
        name='workout-exercise-list-create'
    ),

    path(
        'workout-exercises/<int:pk>/',
        WorkoutExerciseDetailView.as_view(),
        name='workout-exercise-detail'
    ),

    # =====================================================
    # Workout Sets
    # =====================================================

    path(
        'exercises/<int:exercise_id>/sets/',
        WorkoutSetListCreateView.as_view(),
        name='workout-set-list-create'
    ),

    path(
        'workout-sets/<int:pk>/',
        WorkoutSetDetailView.as_view(),
        name='workout-set-detail'
    ),

    # =====================================================
    # Workout Sessions
    # =====================================================

    path(
        'sessions/',
        WorkoutSessionListCreateView.as_view(),
        name='workout-session-list-create'
    ),

    path(
        'sessions/<int:pk>/',
        WorkoutSessionDetailView.as_view(),
        name='workout-session-detail'
    ),

    path(
        'days/<int:day_id>/start/',
        WorkoutSessionStartView.as_view(),
        name='workout-session-start'
    ),

    path(
        'sessions/<int:pk>/finish/',
        WorkoutSessionFinishView.as_view(),
        name='workout-session-finish'
    ),

    # =====================================================
    # Workout Logs
    # =====================================================

    path(
        'sessions/<int:session_id>/logs/',
        WorkoutLogListCreateView.as_view(),
        name='workout-log-list-create'
    ),

    # =====================================================
    # Workout Log Sets
    # =====================================================

    path(
        'logs/<int:log_id>/sets/',
        WorkoutLogSetListCreateView.as_view(),
        name='workout-log-set-list-create'
    ),
]