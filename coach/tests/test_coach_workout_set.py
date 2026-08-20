
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from exercises.models import Exercise
from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSet,
)


class CoachWorkoutSetTests(APITestCase):

    def setUp(self):

        # =====================================================
        # Coach 1
        # =====================================================

        self.coach = User.objects.create_user(
            username='coach',
            email='coach@test.com',
            password='12345678',
            role='coach',
        )

        # =====================================================
        # Coach 2
        # =====================================================

        self.other_coach = User.objects.create_user(
            username='other_coach',
            email='othercoach@test.com',
            password='12345678',
            role='coach',
        )

        # =====================================================
        # Athlete
        # =====================================================

        self.athlete = User.objects.create_user(
            username='athlete',
            email='athlete@test.com',
            password='12345678',
            role='athlete',
        )

        # =====================================================
        # Workout Plan
        # =====================================================

        self.plan = WorkoutPlan.objects.create(
            name='Test Workout Plan',
            description='Test plan',
            athlete=self.athlete,
            coach=self.coach,
        )

        # =====================================================
        # Workout Day
        # =====================================================

        self.day = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=1,
            name='Chest Day',
            description='Chest workout',
        )

        # =====================================================
        # Exercise
        # =====================================================

        self.exercise = Exercise.objects.create(
            external_id='test-001',
            name='Bench Press',
            slug='bench-press-test',
            category='strength',
            body_part='chest',
            equipment='barbell',
            target_muscle='chest',
            muscle_group='chest',
        )

        # =====================================================
        # Workout Exercise
        # =====================================================

        self.workout_exercise = WorkoutExercise.objects.create(
            workout_day=self.day,
            exercise=self.exercise,
            order=1,
            notes='Main chest exercise',
        )

        # =====================================================
        # Existing Set
        # =====================================================

        self.workout_set = WorkoutSet.objects.create(
            workout_exercise=self.workout_exercise,
            set_number=1,
            repetitions=10,
            weight=Decimal('50.00'),
            rest_seconds=90,
            notes='First set',
        )

        # =====================================================
        # URLs
        # =====================================================

        self.list_url = reverse(
            'coach-workout-sets',
            kwargs={
                'exercise_id': self.workout_exercise.id
            }
        )

        self.detail_url = reverse(
            'coach-workout-set-detail',
            kwargs={
                'set_id': self.workout_set.id
            }
        )

        self.client.force_authenticate(
            user=self.coach
        )

    # =========================================================
    # Create
    # =========================================================

    def test_create_workout_set(self):

        data = {
            'set_number': 2,
            'repetitions': 8,
            'weight': '60.00',
            'rest_seconds': 120,
            'notes': 'Second set',
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            WorkoutSet.objects.count(),
            2
        )

        workout_set = WorkoutSet.objects.get(
            set_number=2
        )

        self.assertEqual(
            workout_set.workout_exercise,
            self.workout_exercise
        )

        self.assertEqual(
            workout_set.repetitions,
            8
        )

        self.assertEqual(
            workout_set.weight,
            Decimal('60.00')
        )

    # =========================================================
    # List
    # =========================================================

    def test_list_workout_sets(self):

        WorkoutSet.objects.create(
            workout_exercise=self.workout_exercise,
            set_number=2,
            repetitions=8,
            weight=Decimal('55.00'),
            rest_seconds=90,
        )

        response = self.client.get(
            self.list_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

        self.assertEqual(
            response.data[0]['set_number'],
            1
        )

        self.assertEqual(
            response.data[1]['set_number'],
            2
        )

    # =========================================================
    # Update
    # =========================================================

    def test_update_workout_set(self):

        data = {
            'set_number': 1,
            'repetitions': 12,
            'weight': '65.00',
            'rest_seconds': 120,
            'notes': 'Updated set',
        }

        response = self.client.put(
            self.detail_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.workout_set.refresh_from_db()

        self.assertEqual(
            self.workout_set.repetitions,
            12
        )

        self.assertEqual(
            self.workout_set.weight,
            Decimal('65.00')
        )

        self.assertEqual(
            self.workout_set.rest_seconds,
            120
        )

        self.assertEqual(
            self.workout_set.notes,
            'Updated set'
        )

    # =========================================================
    # Patch
    # =========================================================

    def test_patch_workout_set(self):

        response = self.client.patch(
            self.detail_url,
            {
                'weight': '70.00'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.workout_set.refresh_from_db()

        self.assertEqual(
            self.workout_set.weight,
            Decimal('70.00')
        )

        self.assertEqual(
            self.workout_set.repetitions,
            10
        )

    # =========================================================
    # Delete
    # =========================================================

    def test_delete_workout_set(self):

        response = self.client.delete(
            self.detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            WorkoutSet.objects.filter(
                id=self.workout_set.id
            ).exists()
        )

    # =========================================================
    # Invalid Set Number
    # =========================================================

    def test_create_set_with_invalid_set_number(self):

        data = {
            'set_number': 0,
            'repetitions': 10,
            'weight': '50.00',
            'rest_seconds': 90,
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'set_number',
            response.data
        )

    # =========================================================
    # Invalid Repetitions
    # =========================================================

    def test_create_set_with_invalid_repetitions(self):

        data = {
            'set_number': 2,
            'repetitions': 0,
            'weight': '50.00',
            'rest_seconds': 90,
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'repetitions',
            response.data
        )

    # =========================================================
    # Negative Weight
    # =========================================================

    def test_create_set_with_negative_weight(self):

        data = {
            'set_number': 2,
            'repetitions': 10,
            'weight': '-5.00',
            'rest_seconds': 90,
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'weight',
            response.data
        )

    # =========================================================
    # Negative Rest
    # =========================================================

    def test_create_set_with_negative_rest(self):

        data = {
            'set_number': 2,
            'repetitions': 10,
            'weight': '50.00',
            'rest_seconds': -10,
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'rest_seconds',
            response.data
        )

    # =========================================================
    # Duplicate Set Number
    # =========================================================

    def test_create_duplicate_set_number(self):

        data = {
            'set_number': 1,
            'repetitions': 8,
            'weight': '60.00',
            'rest_seconds': 90,
        }

        response = self.client.post(
            self.list_url,
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'set_number',
            response.data
        )

    # =========================================================
    # Update To Duplicate Set Number
    # =========================================================

    def test_update_set_to_duplicate_set_number(self):

        second_set = WorkoutSet.objects.create(
            workout_exercise=self.workout_exercise,
            set_number=2,
            repetitions=8,
            weight=Decimal('55.00'),
            rest_seconds=90,
        )

        url = reverse(
            'coach-workout-set-detail',
            kwargs={
                'set_id': second_set.id
            }
        )

        response = self.client.patch(
            url,
            {
                'set_number': 1
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'set_number',
            response.data
        )

    # =========================================================
    # Coach Cannot Access Another Coach Set
    # =========================================================

    def test_coach_cannot_access_another_coach_set(self):

        other_plan = WorkoutPlan.objects.create(
            name='Other Coach Plan',
            description='Other plan',
            athlete=self.athlete,
            coach=self.other_coach,
        )

        other_day = WorkoutDay.objects.create(
            workout_plan=other_plan,
            day_number=1,
            name='Other Day',
        )

        other_workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=other_day,
                exercise=self.exercise,
                order=1,
            )
        )

        other_set = WorkoutSet.objects.create(
            workout_exercise=other_workout_exercise,
            set_number=1,
            repetitions=10,
            weight=Decimal('50.00'),
            rest_seconds=90,
        )

        detail_url = reverse(
            'coach-workout-set-detail',
            kwargs={
                'set_id': other_set.id
            }
        )

        response = self.client.get(
            detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # Coach Cannot Create Set For Another Coach Exercise
    # =========================================================

    def test_coach_cannot_create_set_for_another_coach_exercise(
        self
    ):

        other_plan = WorkoutPlan.objects.create(
            name='Other Coach Plan',
            athlete=self.athlete,
            coach=self.other_coach,
        )

        other_day = WorkoutDay.objects.create(
            workout_plan=other_plan,
            day_number=1,
            name='Other Day',
        )

        other_workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=other_day,
                exercise=self.exercise,
                order=1,
            )
        )

        url = reverse(
            'coach-workout-sets',
            kwargs={
                'exercise_id': other_workout_exercise.id
            }
        )

        response = self.client.post(
            url,
            {
                'set_number': 1,
                'repetitions': 10,
                'weight': '50.00',
                'rest_seconds': 90,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # Set Belongs To Correct Exercise
    # =========================================================

    def test_created_set_belongs_to_correct_exercise(self):

        response = self.client.post(
            self.list_url,
            {
                'set_number': 2,
                'repetitions': 10,
                'weight': '50.00',
                'rest_seconds': 90,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        created_set = WorkoutSet.objects.get(
            set_number=2
        )

        self.assertEqual(
            created_set.workout_exercise_id,
            self.workout_exercise.id
        )
