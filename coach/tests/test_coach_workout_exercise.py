from datetime import date

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    AthleteProfile,
    CoachProfile,
)

from exercises.models import Exercise

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
)


User = get_user_model()


class CoachWorkoutExerciseTestCase(APITestCase):

    def setUp(self):

        # =====================================================
        # Coach
        # =====================================================

        self.coach = User.objects.create_user(
            username='exercise_coach',
            email='exercise_coach@test.com',
            password='TestPassword123',
            role='coach'
        )

        CoachProfile.objects.create(
            user=self.coach,
            bio='Test Coach',
            specialization='Bodybuilding',
            experience_years=5
        )

        # =====================================================
        # Another Coach
        # =====================================================

        self.other_coach = User.objects.create_user(
            username='other_exercise_coach',
            email='other_exercise_coach@test.com',
            password='TestPassword123',
            role='coach'
        )

        CoachProfile.objects.create(
            user=self.other_coach,
            bio='Other Coach',
            specialization='Fitness',
            experience_years=3
        )

        # =====================================================
        # Athlete
        # =====================================================

        self.athlete = User.objects.create_user(
            username='exercise_athlete',
            email='exercise_athlete@test.com',
            password='TestPassword123',
            role='athlete'
        )

        self.profile = AthleteProfile.objects.create(
            user=self.athlete,
            gender='male',
            birth_date=date(2000, 1, 1),
            height='180.00',
            goal='muscle_gain',
            activity_level='moderate'
        )

        # =====================================================
        # Other Athlete
        # =====================================================

        self.other_athlete = User.objects.create_user(
            username='other_exercise_athlete',
            email='other_exercise_athlete@test.com',
            password='TestPassword123',
            role='athlete'
        )

        AthleteProfile.objects.create(
            user=self.other_athlete,
            gender='male',
            height='175.00',
            goal='weight_loss',
            activity_level='light'
        )

        # =====================================================
        # Workout Plan
        # =====================================================

        self.plan = WorkoutPlan.objects.create(
            name='Exercise Test Plan',
            description='Plan for exercise tests',
            athlete=self.athlete,
            coach=self.coach,
            is_active=True
        )

        # =====================================================
        # Workout Day
        # =====================================================

        self.day = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=1,
            name='Chest Day',
            description='Chest workout'
        )

        # =====================================================
        # Another Coach Plan
        # =====================================================

        self.other_plan = WorkoutPlan.objects.create(
            name='Other Coach Plan',
            description='Another coach plan',
            athlete=self.other_athlete,
            coach=self.other_coach,
            is_active=True
        )

        self.other_day = WorkoutDay.objects.create(
            workout_plan=self.other_plan,
            day_number=1,
            name='Other Day',
            description='Other workout day'
        )

        # =====================================================
        # Exercises
        # =====================================================

        self.exercise = Exercise.objects.create(
            external_id='test-bench-001',
            name='Bench Press',
            slug='bench-press'
        )

        self.exercise_2 = Exercise.objects.create(
            external_id='test-squat-002',
            name='Squat',
            slug='squat'
        )

        self.exercise_3 = Exercise.objects.create(
            external_id='test-deadlift-003',
            name='Deadlift',
            slug='deadlift'
        )

        # =====================================================
        # Existing Workout Exercise
        # =====================================================

        self.workout_exercise = WorkoutExercise.objects.create(
            workout_day=self.day,
            exercise=self.exercise,
            order=1,
            notes='Main chest exercise'
        )

    # =========================================================
    # Login
    # =========================================================

    def login(self, user):

        response = self.client.post(
            '/api/auth/token/',
            {
                'username': user.username,
                'password': 'TestPassword123'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['access']}"
            )
        )

    # =========================================================
    # 01 - Coach can list exercises
    # =========================================================

    def test_01_coach_can_list_exercises(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/days/'
            f'{self.day.id}/exercises/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['id'],
            self.workout_exercise.id
        )

        self.assertEqual(
            response.data[0]['exercise'],
            self.exercise.id
        )

        self.assertEqual(
            response.data[0]['exercise_name'],
            'Bench Press'
        )

        self.assertEqual(
            response.data[0]['order'],
            1
        )

    # =========================================================
    # 02 - Coach can create exercise
    # =========================================================

    def test_02_coach_can_create_exercise(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/days/'
            f'{self.day.id}/exercises/',
            {
                'exercise': self.exercise_2.id,
                'order': 2,
                'notes': 'Second exercise'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['exercise'],
            self.exercise_2.id
        )

        self.assertEqual(
            response.data['order'],
            2
        )

        self.assertEqual(
            response.data['exercise_name'],
            'Squat'
        )

        self.assertEqual(
            response.data['notes'],
            'Second exercise'
        )

        self.assertTrue(
            WorkoutExercise.objects.filter(
                workout_day=self.day,
                exercise=self.exercise_2,
                order=2
            ).exists()
        )

    # =========================================================
    # 03 - Coach cannot access another coach's day
    # =========================================================

    def test_03_coach_cannot_access_other_coach_day(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/days/'
            f'{self.other_day.id}/exercises/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 04 - Athlete cannot access exercise API
    # =========================================================

    def test_04_athlete_cannot_access_exercise_api(self):

        self.login(self.athlete)

        response = self.client.get(
            f'/api/coach/days/'
            f'{self.day.id}/exercises/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 05 - Unauthenticated user cannot access API
    # =========================================================

    def test_05_unauthenticated_user_cannot_access_exercise_api(
        self
    ):

        response = self.client.get(
            f'/api/coach/days/'
            f'{self.day.id}/exercises/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # =========================================================
    # 06 - Coach can update exercise
    # =========================================================

    def test_06_coach_can_update_exercise(self):

        self.login(self.coach)

        response = self.client.patch(
            f'/api/coach/exercises/'
            f'{self.workout_exercise.id}/',
            {
                'order': 3,
                'notes': 'Updated notes'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['order'],
            3
        )

        self.assertEqual(
            response.data['notes'],
            'Updated notes'
        )

        self.workout_exercise.refresh_from_db()

        self.assertEqual(
            self.workout_exercise.order,
            3
        )

        self.assertEqual(
            self.workout_exercise.notes,
            'Updated notes'
        )

    # =========================================================
    # 07 - Coach can delete exercise
    # =========================================================

    def test_07_coach_can_delete_exercise(self):

        self.login(self.coach)

        response = self.client.delete(
            f'/api/coach/exercises/'
            f'{self.workout_exercise.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            WorkoutExercise.objects.filter(
                id=self.workout_exercise.id
            ).exists()
        )

    # =========================================================
    # 08 - Duplicate order is invalid
    # =========================================================

    def test_08_duplicate_order_is_invalid(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/days/'
            f'{self.day.id}/exercises/',
            {
                'exercise': self.exercise_2.id,
                'order': 1,
                'notes': 'Duplicate order'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'order',
            response.data
        )

    # =========================================================
    # 09 - Invalid order
    # =========================================================

    def test_09_invalid_order(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/days/'
            f'{self.day.id}/exercises/',
            {
                'exercise': self.exercise_2.id,
                'order': 0,
                'notes': 'Invalid order'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'order',
            response.data
        )

    # =========================================================
    # 10 - Cannot create exercise on another coach's day
    # =========================================================

    def test_10_coach_cannot_create_exercise_on_other_coach_day(
        self
    ):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/days/'
            f'{self.other_day.id}/exercises/',
            {
                'exercise': self.exercise_2.id,
                'order': 2,
                'notes': 'Unauthorized exercise'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 11 - Coach cannot update another coach's exercise
    # =========================================================

    def test_11_coach_cannot_update_other_coach_exercise(
        self
    ):

        other_workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=self.other_day,
                exercise=self.exercise_3,
                order=1,
                notes='Other coach exercise'
            )
        )

        self.login(self.coach)

        response = self.client.patch(
            f'/api/coach/exercises/'
            f'{other_workout_exercise.id}/',
            {
                'order': 2,
                'notes': 'Hacked'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 12 - Coach cannot delete another coach's exercise
    # =========================================================

    def test_12_coach_cannot_delete_other_coach_exercise(
        self
    ):

        other_workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=self.other_day,
                exercise=self.exercise_3,
                order=1,
                notes='Other coach exercise'
            )
        )

        self.login(self.coach)

        response = self.client.delete(
            f'/api/coach/exercises/'
            f'{other_workout_exercise.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            WorkoutExercise.objects.filter(
                id=other_workout_exercise.id
            ).exists()
        )

    # =========================================================
    # 13 - Exercise is required
    # =========================================================

    def test_13_exercise_is_required(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/days/'
            f'{self.day.id}/exercises/',
            {
                'order': 2,
                'notes': 'No exercise'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'exercise',
            response.data
        )

    # =========================================================
    # 14 - Order is required
    # =========================================================

    def test_14_order_is_required(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/days/'
            f'{self.day.id}/exercises/',
            {
                'exercise': self.exercise_2.id,
                'notes': 'No order'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'order',
            response.data
        )