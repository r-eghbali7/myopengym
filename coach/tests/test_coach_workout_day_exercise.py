from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from accounts.models import User
from exercises.models import Exercise
from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
)


class CoachWorkoutDayExerciseTests(TestCase):

    def setUp(self):

        self.client = APIClient()

        # =========================================
        # Coach
        # =========================================

        self.coach = User.objects.create_user(
            username='coach',
            email='coach@test.com',
            password='12345678',
            role='coach'
        )

        # =========================================
        # Athlete
        # =========================================

        self.athlete = User.objects.create_user(
            username='athlete',
            email='athlete@test.com',
            password='12345678'
        )

        # =========================================
        # Login
        # =========================================

        self.client.force_authenticate(
            user=self.coach
        )

        # =========================================
        # Exercise
        # =========================================

        self.exercise = Exercise.objects.create(
            external_id='test-001',
            name='Bench Press',
            slug='bench-press',
            category='strength',
            body_part='chest',
            equipment='barbell',
            target_muscle='chest',
            muscle_group='chest',
        )

        # =========================================
        # Workout Plan
        # =========================================

        self.plan = WorkoutPlan.objects.create(
            name='Test Workout Plan',
            description='Test plan',
            athlete=self.athlete,
            coach=self.coach,
        )

        # =========================================
        # Workout Day
        # =========================================

        self.day = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=1,
            name='Chest Day',
            description='Chest workout',
        )

    # =====================================================
    # Workout Day
    # =====================================================

    def test_create_workout_day(self):

        url = reverse(
            'coach-workout-days',
            kwargs={
                'plan_id': self.plan.id
            }
        )

        response = self.client.post(
            url,
            {
                'day_number': 2,
                'name': 'Back Day',
                'description': 'Back workout',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertTrue(
            WorkoutDay.objects.filter(
                workout_plan=self.plan,
                day_number=2
            ).exists()
        )

    def test_create_duplicate_workout_day(self):

        url = reverse(
            'coach-workout-days',
            kwargs={
                'plan_id': self.plan.id
            }
        )

        response = self.client.post(
            url,
            {
                'day_number': 1,
                'name': 'Another Day',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_create_workout_day_with_invalid_day_number(self):

        url = reverse(
            'coach-workout-days',
            kwargs={
                'plan_id': self.plan.id
            }
        )

        response = self.client.post(
            url,
            {
                'day_number': 0,
                'name': 'Invalid Day',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_list_workout_days(self):

        url = reverse(
            'coach-workout-days',
            kwargs={
                'plan_id': self.plan.id
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['day_number'],
            1
        )

    def test_update_workout_day(self):

        url = reverse(
            'coach-workout-day-detail',
            kwargs={
                'plan_id': self.plan.id,
                'day_id': self.day.id,
            }
        )

        response = self.client.patch(
            url,
            {
                'name': 'Updated Chest Day'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.day.refresh_from_db()

        self.assertEqual(
            self.day.name,
            'Updated Chest Day'
        )

    def test_delete_workout_day(self):

        url = reverse(
            'coach-workout-day-detail',
            kwargs={
                'plan_id': self.plan.id,
                'day_id': self.day.id,
            }
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            204
        )

        self.assertFalse(
            WorkoutDay.objects.filter(
                id=self.day.id
            ).exists()
        )

    # =====================================================
    # Workout Exercise
    # =====================================================

    def test_create_workout_exercise(self):

        url = reverse(
            'coach-workout-exercises',
            kwargs={
                'day_id': self.day.id
            }
        )

        response = self.client.post(
            url,
            {
                'exercise': self.exercise.id,
                'order': 1,
                'notes': 'Use controlled movement',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertTrue(
            WorkoutExercise.objects.filter(
                workout_day=self.day,
                exercise=self.exercise,
                order=1
            ).exists()
        )

    def test_create_duplicate_exercise_order(self):

        WorkoutExercise.objects.create(
            workout_day=self.day,
            exercise=self.exercise,
            order=1,
        )

        second_exercise = Exercise.objects.create(
            external_id='test-002',
            name='Incline Bench Press',
            slug='incline-bench-press',
        )

        url = reverse(
            'coach-workout-exercises',
            kwargs={
                'day_id': self.day.id
            }
        )

        response = self.client.post(
            url,
            {
                'exercise': second_exercise.id,
                'order': 1,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_create_exercise_with_invalid_order(self):

        url = reverse(
            'coach-workout-exercises',
            kwargs={
                'day_id': self.day.id
            }
        )

        response = self.client.post(
            url,
            {
                'exercise': self.exercise.id,
                'order': 0,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_list_workout_exercises(self):

        WorkoutExercise.objects.create(
            workout_day=self.day,
            exercise=self.exercise,
            order=1,
        )

        url = reverse(
            'coach-workout-exercises',
            kwargs={
                'day_id': self.day.id
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['exercise'],
            self.exercise.id
        )

        self.assertEqual(
            response.data[0]['exercise_name'],
            'Bench Press'
        )

    def test_update_workout_exercise(self):

        workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=self.day,
                exercise=self.exercise,
                order=1,
                notes='Old notes',
            )
        )

        url = reverse(
            'coach-workout-exercise-detail',
            kwargs={
                'exercise_id': workout_exercise.id
            }
        )

        response = self.client.patch(
            url,
            {
                'notes': 'Updated notes'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        workout_exercise.refresh_from_db()

        self.assertEqual(
            workout_exercise.notes,
            'Updated notes'
        )

    def test_delete_workout_exercise(self):

        workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=self.day,
                exercise=self.exercise,
                order=1,
            )
        )

        url = reverse(
            'coach-workout-exercise-detail',
            kwargs={
                'exercise_id': workout_exercise.id
            }
        )

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            204
        )

        self.assertFalse(
            WorkoutExercise.objects.filter(
                id=workout_exercise.id
            ).exists()
        )

    # =====================================================
    # Security
    # =====================================================

    def test_coach_cannot_access_another_coach_workout_day(self):

        another_coach = User.objects.create_user(
            username='another_coach',
            email='another@test.com',
            password='12345678'
        )

        another_plan = WorkoutPlan.objects.create(
            name='Another Plan',
            athlete=self.athlete,
            coach=another_coach,
        )

        another_day = WorkoutDay.objects.create(
            workout_plan=another_plan,
            day_number=1,
            name='Another Day',
        )

        url = reverse(
            'coach-workout-day-detail',
            kwargs={
                'plan_id': another_plan.id,
                'day_id': another_day.id,
            }
        )

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            404
        )