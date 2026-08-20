from django.urls import path

from .views import (
    CoachAthleteListView,
    CoachAthleteDetailView,
    CoachAthleteProgressView,
    CoachAthleteWorkoutListView,
    CoachWorkoutDayDetailView,
    CoachWorkoutDayListCreateView,
    CoachWorkoutExerciseDetailView,
    CoachWorkoutExerciseListCreateView,
    CoachWorkoutPlanListCreateView,
    CoachWorkoutPlanDetailView,
    CoachWorkoutSetDetailView,
    CoachWorkoutSetListCreateView,
)


urlpatterns = [

    # =====================================================
    # Athletes
    # =====================================================

    path(
        'athletes/',
        CoachAthleteListView.as_view(),
        name='coach-athletes'
    ),

    path(
        'athletes/<int:athlete_id>/',
        CoachAthleteDetailView.as_view(),
        name='coach-athlete-detail'
    ),

    # =====================================================
    # Progress
    # =====================================================

    path(
        'athletes/<int:athlete_id>/progress/',
        CoachAthleteProgressView.as_view(),
        name='coach-athlete-progress'
    ),

    # =====================================================
    # Athlete Workouts
    # =====================================================

    path(
        'athletes/<int:athlete_id>/workouts/',
        CoachAthleteWorkoutListView.as_view(),
        name='coach-athlete-workouts'
    ),

    # =====================================================
    # Workout CRUD
    # =====================================================

    path(
        'workouts/',
        CoachWorkoutPlanListCreateView.as_view(),
        name='coach-workout-list-create'
    ),

    path(
        'workouts/<int:plan_id>/',
        CoachWorkoutPlanDetailView.as_view(),
        name='coach-workout-detail'
    ),

    path(
        'workouts/<int:plan_id>/days/',
        CoachWorkoutDayListCreateView.as_view(),
        name='coach-workout-days'
    ),

    path(
        'workouts/<int:plan_id>/days/<int:day_id>/',
        CoachWorkoutDayDetailView.as_view(),
        name='coach-workout-day-detail'
    ),

    # =====================================================
    # Workout Exercises
    # =====================================================

    path(
        'days/<int:day_id>/exercises/',
        CoachWorkoutExerciseListCreateView.as_view(),
        name='coach-workout-exercises'
    ),

    path(
        'exercises/<int:exercise_id>/',
        CoachWorkoutExerciseDetailView.as_view(),
        name='coach-workout-exercise-detail'
    ),

    # =====================================================
    # Workout Sets
    # =====================================================

    path(
        'exercises/<int:exercise_id>/sets/',
        CoachWorkoutSetListCreateView.as_view(),
        name='coach-workout-sets'
    ),

    path(
        'sets/<int:set_id>/',
        CoachWorkoutSetDetailView.as_view(),
        name='coach-workout-set-detail'
    ),
]