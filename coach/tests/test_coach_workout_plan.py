from datetime import date

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    AthleteProfile,
    CoachProfile,
    CoachAthleteRelation,
)

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
)


User = get_user_model()


class CoachWorkoutPlanTestCase(APITestCase):

    def setUp(self):

        # =====================================================
        # Users
        # =====================================================

        self.coach = User.objects.create_user(
            username='coach1',
            email='coach1@test.com',
            password='testpass123',
        )

        self.other_coach = User.objects.create_user(
            username='coach2',
            email='coach2@test.com',
            password='testpass123',
        )

        self.athlete = User.objects.create_user(
            username='athlete1',
            email='athlete1@test.com',
            password='testpass123',
        )

        self.other_athlete = User.objects.create_user(
            username='athlete2',
            email='athlete2@test.com',
            password='testpass123',
        )

        # =====================================================
        # Profiles
        # =====================================================

        self.coach_profile = CoachProfile.objects.create(
            user=self.coach,
        )

        self.other_coach_profile = CoachProfile.objects.create(
            user=self.other_coach,
        )

        self.athlete_profile = AthleteProfile.objects.create(
            user=self.athlete,
        )

        self.other_athlete_profile = AthleteProfile.objects.create(
            user=self.other_athlete,
        )

        # =====================================================
        # Coach / Athlete Relation
        # =====================================================

        CoachAthleteRelation.objects.create(
            coach=self.coach_profile,
            athlete=self.athlete_profile,
        )

        CoachAthleteRelation.objects.create(
            coach=self.other_coach_profile,
            athlete=self.other_athlete_profile,
        )

        # =====================================================
        # Existing Plans
        # =====================================================

        self.workout_plan = WorkoutPlan.objects.create(
            name='Push Workout',
            description='Chest and shoulders',
            athlete=self.athlete,
            coach=self.coach,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 9, 1),
            is_active=True,
        )

        self.other_workout_plan = WorkoutPlan.objects.create(
            name='Other Coach Plan',
            description='Other athlete workout',
            athlete=self.other_athlete,
            coach=self.other_coach,
            start_date=date(2026, 8, 1),
            end_date=date(2026, 9, 1),
            is_active=True,
        )

        # =====================================================
        # API
        # =====================================================

        self.client.force_authenticate(
            user=self.coach
        )

    # =========================================================
    # Helpers
    # =========================================================

    def authenticate_as_coach(self):

        self.client.force_authenticate(
            user=self.coach
        )

    def authenticate_as_other_coach(self):

        self.client.force_authenticate(
            user=self.other_coach
        )

    def authenticate_as_athlete(self):

        self.client.force_authenticate(
            user=self.athlete
        )

    def unauthenticate(self):

        self.client.force_authenticate(
            user=None
        )

    def get_list_url(self):

        return reverse(
            'coach-workout-list-create'
        )

    def get_detail_url(self, plan_id=None):

        if plan_id is None:
            plan_id = self.workout_plan.id

        return reverse(
            'coach-workout-detail',
            kwargs={
                'plan_id': plan_id
            }
        )

    # =========================================================
    # 01 - Coach can list plans
    # =========================================================

    def test_01_coach_can_list_plans(self):

        self.authenticate_as_coach()

        response = self.client.get(
            self.get_list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    # =========================================================
    # 02 - Coach can retrieve own plan
    # =========================================================

    def test_02_coach_can_retrieve_own_plan(self):

        self.authenticate_as_coach()

        response = self.client.get(
            self.get_detail_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            self.workout_plan.id
        )

    # =========================================================
    # 03 - Coach can create plan for assigned athlete
    # =========================================================

    def test_03_coach_can_create_plan_for_assigned_athlete(self):

        self.authenticate_as_coach()

        data = {
            'name': 'Leg Day',
            'description': 'Leg workout',
            'athlete': self.athlete.id,
            'start_date': '2026-08-20',
            'end_date': '2026-09-20',
            'is_active': True,
        }

        response = self.client.post(
            self.get_list_url(),
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WorkoutPlan.objects.filter(
                name='Leg Day',
                athlete=self.athlete,
                coach=self.coach,
            ).exists()
        )

    # =========================================================
    # 04 - Coach cannot create plan for unrelated athlete
    # =========================================================

    def test_04_coach_cannot_create_plan_for_unrelated_athlete(self):

        self.authenticate_as_coach()

        data = {
            'name': 'Unauthorized Plan',
            'description': 'Should fail',
            'athlete': self.other_athlete.id,
            'start_date': '2026-08-20',
            'end_date': '2026-09-20',
            'is_active': True,
        }

        response = self.client.post(
            self.get_list_url(),
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 05 - Other coach cannot retrieve plan
    # =========================================================

    def test_05_other_coach_cannot_retrieve_plan(self):

        self.authenticate_as_other_coach()

        response = self.client.get(
            self.get_detail_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 06 - Other coach cannot update plan
    # =========================================================

    def test_06_other_coach_cannot_update_plan(self):

        self.authenticate_as_other_coach()

        response = self.client.patch(
            self.get_detail_url(),
            {
                'name': 'Hacked Plan'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.workout_plan.refresh_from_db()

        self.assertEqual(
            self.workout_plan.name,
            'Push Workout'
        )

    # =========================================================
    # 07 - Other coach cannot delete plan
    # =========================================================

    def test_07_other_coach_cannot_delete_plan(self):

        self.authenticate_as_other_coach()

        response = self.client.delete(
            self.get_detail_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            WorkoutPlan.objects.filter(
                pk=self.workout_plan.pk
            ).exists()
        )

    # =========================================================
    # 08 - Coach can update own plan
    # =========================================================

    def test_08_coach_can_update_own_plan(self):

        self.authenticate_as_coach()

        response = self.client.patch(
            self.get_detail_url(),
            {
                'name': 'Updated Push Workout'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.workout_plan.refresh_from_db()

        self.assertEqual(
            self.workout_plan.name,
            'Updated Push Workout'
        )

    # =========================================================
    # 09 - Coach can delete own plan
    # =========================================================

    def test_09_coach_can_delete_own_plan(self):

        self.authenticate_as_coach()

        plan_id = self.workout_plan.id

        response = self.client.delete(
            self.get_detail_url(plan_id)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            WorkoutPlan.objects.filter(
                pk=plan_id
            ).exists()
        )

    # =========================================================
    # 10 - Invalid date range
    # =========================================================

    def test_10_invalid_date_range(self):

        self.authenticate_as_coach()

        data = {
            'name': 'Invalid Plan',
            'description': '',
            'athlete': self.athlete.id,
            'start_date': '2026-09-20',
            'end_date': '2026-08-20',
            'is_active': True,
        }

        response = self.client.post(
            self.get_list_url(),
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'end_date',
            response.data
        )

    # =========================================================
    # 11 - Non-existing plan returns 404
    # =========================================================

    def test_11_non_existing_plan_returns_404(self):

        self.authenticate_as_coach()

        response = self.client.get(
            self.get_detail_url(999999)
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 12 - Athlete cannot list coach plans
    # =========================================================

    def test_12_athlete_cannot_list_plans(self):

        self.authenticate_as_athlete()

        response = self.client.get(
            self.get_list_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 13 - Athlete cannot retrieve plan
    # =========================================================

    def test_13_athlete_cannot_retrieve_plan(self):

        self.authenticate_as_athlete()

        response = self.client.get(
            self.get_detail_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 14 - Athlete cannot update plan
    # =========================================================

    def test_14_athlete_cannot_update_plan(self):

        self.authenticate_as_athlete()

        response = self.client.patch(
            self.get_detail_url(),
            {
                'name': 'Athlete Hacked Plan'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 15 - Athlete cannot delete plan
    # =========================================================

    def test_15_athlete_cannot_delete_plan(self):

        self.authenticate_as_athlete()

        response = self.client.delete(
            self.get_detail_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 16 - Unauthenticated cannot list
    # =========================================================

    def test_16_unauthenticated_cannot_list(self):

        self.unauthenticate()

        response = self.client.get(
            self.get_list_url()
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]
        )

    # =========================================================
    # 17 - Unauthenticated cannot retrieve
    # =========================================================

    def test_17_unauthenticated_cannot_retrieve(self):

        self.unauthenticate()

        response = self.client.get(
            self.get_detail_url()
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]
        )

    # =========================================================
    # 18 - Unauthenticated cannot create
    # =========================================================

    def test_18_unauthenticated_cannot_create(self):

        self.unauthenticate()

        response = self.client.post(
            self.get_list_url(),
            {
                'name': 'Unauthorized',
                'athlete': self.athlete.id,
                'start_date': '2026-08-20',
                'end_date': '2026-09-20',
            },
            format='json'
        )

        self.assertIn(
            response.status_code,
            [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]
        )

    # =========================================================
    # 19 - Plan statistics
    # =========================================================

    def test_19_plan_statistics_are_returned(self):

        WorkoutDay.objects.create(
            workout_plan=self.workout_plan,
            day_number=1,
            name='Chest'
        )

        WorkoutDay.objects.create(
            workout_plan=self.workout_plan,
            day_number=2,
            name='Shoulders'
        )

        self.authenticate_as_coach()

        response = self.client.get(
            self.get_detail_url()
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['total_days'],
            2
        )

        self.assertEqual(
            response.data['total_exercises'],
            0
        )

        self.assertEqual(
            response.data['total_sessions'],
            0
        )
