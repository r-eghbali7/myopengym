from datetime import date

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    AthleteProfile,
    CoachProfile,
    WeightRecord,
)

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSession,
)


User = get_user_model()


class CoachDashboardTestCase(APITestCase):

    def setUp(self):

        # =====================================================
        # Coach
        # =====================================================

        self.coach = User.objects.create_user(
            username='dashboard_coach',
            email='dashboard_coach@test.com',
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
        # Athlete 1
        # =====================================================

        self.athlete = User.objects.create_user(
            username='dashboard_athlete',
            email='dashboard_athlete@test.com',
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
        # Athlete 2
        # =====================================================

        self.other_athlete = User.objects.create_user(
            username='other_athlete',
            email='other_athlete@test.com',
            password='TestPassword123',
            role='athlete'
        )

        self.other_profile = AthleteProfile.objects.create(
            user=self.other_athlete,
            gender='male',
            height='175.00',
            goal='weight_loss',
            activity_level='light'
        )

        # =====================================================
        # Assignment
        # =====================================================

        self.plan = WorkoutPlan.objects.create(
            name='Test Plan',
            description='Coach plan',
            athlete=self.athlete,
            coach=self.coach,
            is_active=True
        )

        # =====================================================
        # Weight
        # =====================================================

        WeightRecord.objects.create(
            athlete=self.profile,
            weight='85.00',
            date=date(2026, 8, 1)
        )

        WeightRecord.objects.create(
            athlete=self.profile,
            weight='82.00',
            date=date(2026, 8, 19)
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
    # 01 - Athlete List
    # =========================================================

    def test_01_coach_can_list_athletes(self):

        self.login(self.coach)

        response = self.client.get(
            '/api/coach/athletes/'
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
            self.profile.id
        )

    # =========================================================
    # 02 - Athlete Detail
    # =========================================================

    def test_02_coach_can_view_athlete(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/athletes/{self.athlete.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['user']['username'],
            'dashboard_athlete'
        )

        self.assertEqual(
            response.data['current_weight'],
            '82.00'
        )

        self.assertEqual(
            response.data['starting_weight'],
            '85.00'
        )

    # =========================================================
    # 03 - Coach cannot see another athlete
    # =========================================================

    def test_03_coach_cannot_view_unassigned_athlete(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/athletes/'
            f'{self.other_athlete.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # 04 - Athlete cannot access dashboard
    # =========================================================

    def test_04_athlete_cannot_access_dashboard(self):

        self.login(self.athlete)

        response = self.client.get(
            '/api/coach/athletes/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 05 - Progress
    # =========================================================

    def test_05_coach_can_view_progress(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/athletes/'
            f'{self.athlete.id}/progress/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['total_plans'],
            1
        )

        self.assertEqual(
            response.data['current_weight'],
            '82.00'
        )

        self.assertEqual(
            response.data['starting_weight'],
            '85.00'
        )

        self.assertEqual(
            response.data['weight_change'],
            '-3.00'
        )

    # =========================================================
    # 06 - Workout Plans
    # =========================================================

    def test_06_coach_can_view_athlete_workouts(self):

        self.login(self.coach)

        response = self.client.get(
            f'/api/coach/athletes/'
            f'{self.athlete.id}/workouts/'
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
            response.data[0]['name'],
            'Test Plan'
        )