
from datetime import date

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    AthleteProfile,
    CoachProfile,
)

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
)


User = get_user_model()


class CoachWorkoutDayTestCase(APITestCase):

    # =========================================================
    # Setup
    # =========================================================

    def setUp(self):

        # -----------------------------------------------------
        # Coach
        # -----------------------------------------------------

        self.coach = User.objects.create_user(
            username='day_coach',
            email='day_coach@test.com',
            password='TestPassword123',
            role='coach'
        )

        CoachProfile.objects.create(
            user=self.coach,
            bio='Test Coach',
            specialization='Bodybuilding',
            experience_years=5
        )

        # -----------------------------------------------------
        # Athlete
        # -----------------------------------------------------

        self.athlete = User.objects.create_user(
            username='day_athlete',
            email='day_athlete@test.com',
            password='TestPassword123',
            role='athlete'
        )

        AthleteProfile.objects.create(
            user=self.athlete,
            gender='male',
            birth_date=date(2000, 1, 1),
            height='180.00',
            goal='muscle_gain',
            activity_level='moderate'
        )

        # -----------------------------------------------------
        # Other Coach
        # -----------------------------------------------------

        self.other_coach = User.objects.create_user(
            username='other_day_coach',
            email='other_day_coach@test.com',
            password='TestPassword123',
            role='coach'
        )

        CoachProfile.objects.create(
            user=self.other_coach,
            bio='Other Coach',
            specialization='Fitness',
            experience_years=3
        )

        # -----------------------------------------------------
        # Other Athlete
        # -----------------------------------------------------

        self.other_athlete = User.objects.create_user(
            username='other_day_athlete',
            email='other_day_athlete@test.com',
            password='TestPassword123',
            role='athlete'
        )

        AthleteProfile.objects.create(
            user=self.other_athlete,
            gender='male',
            birth_date=date(1999, 1, 1),
            height='175.00',
            goal='weight_loss',
            activity_level='active'
        )

        # -----------------------------------------------------
        # Workout Plan
        # -----------------------------------------------------

        self.plan = WorkoutPlan.objects.create(
            name='Muscle Gain Plan',
            description='Test workout plan',
            athlete=self.athlete,
            coach=self.coach,
            start_date=date(2026, 8, 20),
            end_date=date(2026, 9, 20),
            is_active=True
        )

        # -----------------------------------------------------
        # Other Coach Plan
        # -----------------------------------------------------

        self.other_plan = WorkoutPlan.objects.create(
            name='Other Coach Plan',
            description='Other coach workout plan',
            athlete=self.other_athlete,
            coach=self.other_coach,
            start_date=date(2026, 8, 20),
            end_date=date(2026, 9, 20),
            is_active=True
        )

        # -----------------------------------------------------
        # Existing Days
        # -----------------------------------------------------

        self.day1 = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=1,
            name='Chest',
            description='Chest workout'
        )

        self.day2 = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=2,
            name='Back',
            description='Back workout'
        )

        # -----------------------------------------------------
        # Other Plan Day
        # -----------------------------------------------------

        self.other_day = WorkoutDay.objects.create(
            workout_plan=self.other_plan,
            day_number=1,
            name='Other Chest',
            description='Other coach chest workout'
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
    # 01 - Coach Can List Days
    # =========================================================

    def test_01_coach_can_list_days(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
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
            response.data[0]['day_number'],
            1
        )

        self.assertEqual(
            response.data[0]['name'],
            'Chest'
        )

        self.assertEqual(
            response.data[1]['day_number'],
            2
        )

    # =========================================================
    # 02 - Coach Can Create Day
    # =========================================================

    def test_02_coach_can_create_day(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': 3,
                'name': 'Legs',
                'description': 'Leg workout'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WorkoutDay.objects.filter(
                workout_plan=self.plan,
                day_number=3,
                name='Legs'
            ).exists()
        )

    # =========================================================
    # 03 - Created Day Belongs To Correct Plan
    # =========================================================

    def test_03_created_day_belongs_to_correct_plan(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': 3,
                'name': 'Legs',
                'description': 'Leg workout'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        day = WorkoutDay.objects.get(
            day_number=3,
            workout_plan=self.plan
        )

        self.assertEqual(
            day.workout_plan_id,
            self.plan.id
        )

    # =========================================================
    # 04 - Athlete Cannot List Days
    # =========================================================

    def test_04_athlete_cannot_list_days(self):

        self.login(self.athlete)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 05 - Athlete Cannot Create Day
    # =========================================================

    def test_05_athlete_cannot_create_day(self):

        self.login(self.athlete)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': 3,
                'name': 'Legs'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 06 - Coach Can Retrieve Day
    # =========================================================

    def test_06_coach_can_retrieve_day(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            self.day1.id
        )

        self.assertEqual(
            response.data['day_number'],
            1
        )

        self.assertEqual(
            response.data['name'],
            'Chest'
        )

    # =========================================================
    # 07 - Coach Can Update Day
    # =========================================================

    def test_07_coach_can_update_day(self):

        self.login(self.coach)

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/',
            {
                'name': 'Chest + Triceps'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.day1.refresh_from_db()

        self.assertEqual(
            self.day1.name,
            'Chest + Triceps'
        )

    # =========================================================
    # 08 - Coach Can Update Description
    # =========================================================

    def test_08_coach_can_update_description(self):

        self.login(self.coach)

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/',
            {
                'description': 'Updated chest workout'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.day1.refresh_from_db()

        self.assertEqual(
            self.day1.description,
            'Updated chest workout'
        )

    # =========================================================
    # 09 - Coach Can Delete Day
    # =========================================================

    def test_09_coach_can_delete_day(self):

        self.login(self.coach)

        response = self.client.delete(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            WorkoutDay.objects.filter(
                id=self.day1.id
            ).exists()
        )

    # =========================================================
    # 10 - Other Coach Cannot List Days
    # =========================================================

    def test_10_other_coach_cannot_list_days(self):

        self.login(self.other_coach)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 11 - Other Coach Cannot Retrieve Day
    # =========================================================

    def test_11_other_coach_cannot_retrieve_day(self):

        self.login(self.other_coach)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 12 - Other Coach Cannot Create Day
    # =========================================================

    def test_12_other_coach_cannot_create_day(self):

        self.login(self.other_coach)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': 3,
                'name': 'Legs'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 13 - Other Coach Cannot Update Day
    # =========================================================

    def test_13_other_coach_cannot_update_day(self):

        self.login(self.other_coach)

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/',
            {
                'name': 'Hacked Day'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.day1.refresh_from_db()

        self.assertEqual(
            self.day1.name,
            'Chest'
        )

    # =========================================================
    # 14 - Other Coach Cannot Delete Day
    # =========================================================

    def test_14_other_coach_cannot_delete_day(self):

        self.login(self.other_coach)

        response = self.client.delete(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            WorkoutDay.objects.filter(
                id=self.day1.id
            ).exists()
        )

    # =========================================================
    # 15 - Athlete Cannot Retrieve Day
    # =========================================================

    def test_15_athlete_cannot_retrieve_day(self):

        self.login(self.athlete)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 16 - Athlete Cannot Update Day
    # =========================================================

    def test_16_athlete_cannot_update_day(self):

        self.login(self.athlete)

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/',
            {
                'name': 'Athlete Updated'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.day1.refresh_from_db()

        self.assertEqual(
            self.day1.name,
            'Chest'
        )

    # =========================================================
    # 17 - Athlete Cannot Delete Day
    # =========================================================

    def test_17_athlete_cannot_delete_day(self):

        self.login(self.athlete)

        response = self.client.delete(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        self.assertTrue(
            WorkoutDay.objects.filter(
                id=self.day1.id
            ).exists()
        )

    # =========================================================
    # 18 - Duplicate Day Number Is Invalid
    # =========================================================

    def test_18_duplicate_day_number_is_invalid(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': 1,
                'name': 'Another Chest'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertFalse(
            WorkoutDay.objects.filter(
                workout_plan=self.plan,
                name='Another Chest'
            ).exists()
        )

    # =========================================================
    # 19 - Invalid Day Number
    # =========================================================

    def test_19_invalid_day_number(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': 0,
                'name': 'Invalid Day'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # =========================================================
    # 20 - Negative Day Number
    # =========================================================

    def test_20_negative_day_number(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': -1,
                'name': 'Invalid Day'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # =========================================================
    # 21 - Update To Existing Day Number Is Invalid
    # =========================================================

    def test_21_update_to_existing_day_number_is_invalid(self):

        self.login(self.coach)

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day2.id}/',
            {
                'day_number': 1
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.day2.refresh_from_db()

        self.assertEqual(
            self.day2.day_number,
            2
        )

    # =========================================================
    # 22 - Same Day Number On Same Instance Is Valid
    # =========================================================

    def test_22_same_day_number_on_same_instance_is_valid(self):

        self.login(self.coach)

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/',
            {
                'day_number': 1,
                'name': 'Updated Chest'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.day1.refresh_from_db()

        self.assertEqual(
            self.day1.day_number,
            1
        )

        self.assertEqual(
            self.day1.name,
            'Updated Chest'
        )

    # =========================================================
    # 23 - Non Existing Plan Returns 404
    # =========================================================

    def test_23_non_existing_plan_returns_404(self):

        self.login(self.coach)

        response = self.client.get(
            '/api/coach/workouts/999999/days/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 24 - Non Existing Day Returns 404
    # =========================================================

    def test_24_non_existing_day_returns_404(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'999999/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 25 - Day From Another Plan Cannot Be Accessed
    # =========================================================

    def test_25_day_from_another_plan_cannot_be_accessed(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.other_day.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 26 - Day From Another Plan Cannot Be Updated
    # =========================================================

    def test_26_day_from_another_plan_cannot_be_updated(self):

        self.login(self.coach)

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.other_day.id}/',
            {
                'name': 'Unauthorized Update'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.other_day.refresh_from_db()

        self.assertEqual(
            self.other_day.name,
            'Other Chest'
        )

    # =========================================================
    # 27 - Day From Another Plan Cannot Be Deleted
    # =========================================================

    def test_27_day_from_another_plan_cannot_be_deleted(self):

        self.login(self.coach)

        response = self.client.delete(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.other_day.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            WorkoutDay.objects.filter(
                id=self.other_day.id
            ).exists()
        )

    # =========================================================
    # 28 - Unauthenticated Cannot List Days
    # =========================================================

    def test_28_unauthenticated_cannot_list_days(self):

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # =========================================================
    # 29 - Unauthenticated Cannot Retrieve Day
    # =========================================================

    def test_29_unauthenticated_cannot_retrieve_day(self):

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # =========================================================
    # 30 - Unauthenticated Cannot Create Day
    # =========================================================

    def test_30_unauthenticated_cannot_create_day(self):

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': 3,
                'name': 'Unauthorized Day'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # =========================================================
    # 31 - Unauthenticated Cannot Update Day
    # =========================================================

    def test_31_unauthenticated_cannot_update_day(self):

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/',
            {
                'name': 'Unauthorized Update'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # =========================================================
    # 32 - Unauthenticated Cannot Delete Day
    # =========================================================

    def test_32_unauthenticated_cannot_delete_day(self):

        response = self.client.delete(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day1.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertTrue(
            WorkoutDay.objects.filter(
                id=self.day1.id
            ).exists()
        )

    # =========================================================
    # 33 - Required Day Number
    # =========================================================

    def test_33_day_number_is_required(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'name': 'No Number Day'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # =========================================================
    # 34 - Multiple Days Are Ordered By Day Number
    # =========================================================

    def test_34_days_are_ordered_by_day_number(self):

        WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=5,
            name='Shoulders',
            description='Shoulder workout'
        )

        WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=3,
            name='Legs',
            description='Leg workout'
        )

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        day_numbers = [
            item['day_number']
            for item in response.data
        ]

        self.assertEqual(
            day_numbers,
            [1, 2, 3, 5]
        )

    # =========================================================
    # 35 - Create Day Without Optional Description
    # =========================================================

    def test_35_create_day_without_description(self):

        self.login(self.coach)

        response = self.client.post(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/',
            {
                'day_number': 3,
                'name': 'Legs'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        day = WorkoutDay.objects.get(
            workout_plan=self.plan,
            day_number=3
        )

        self.assertEqual(
            day.name,
            'Legs'
        )

    # =========================================================
    # 36 - Update Day Number To New Valid Number
    # =========================================================

    def test_36_update_day_number_to_new_valid_number(self):

        self.login(self.coach)

        response = self.client.patch(
            f'/api/coach/workouts/'
            f'{self.plan.id}/days/'
            f'{self.day2.id}/',
            {
                'day_number': 3
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.day2.refresh_from_db()

        self.assertEqual(
            self.day2.day_number,
            3
        )
