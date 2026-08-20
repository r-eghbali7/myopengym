from datetime import date, timedelta

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    AthleteProfile,
    CoachProfile,
    WeightRecord,
)


User = get_user_model()


class AthleteProfileAPITestCase(APITestCase):

    def setUp(self):

        # =====================================================
        # Athlete
        # =====================================================

        self.athlete = User.objects.create_user(
            username='test_athlete',
            email='athlete@test.com',
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
        # Coach
        # =====================================================

        self.coach = User.objects.create_user(
            username='test_coach',
            email='coach@test.com',
            password='TestPassword123',
            role='coach'
        )

        CoachProfile.objects.create(
            user=self.coach,
            bio='Test coach',
            specialization='Bodybuilding',
            experience_years=5
        )

    # =========================================================
    # Helper
    # =========================================================

    def login(self, user):

        response = self.client.post(
            '/api/auth/token/',
            {
                'username': user.username,
                'password': 'TestPassword123',
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
    # 01 - Get Athlete Profile
    # =========================================================

    def test_01_get_athlete_profile(self):

        self.login(self.athlete)

        response = self.client.get(
            '/api/accounts/profile/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['gender'],
            'male'
        )

        self.assertEqual(
            response.data['height'],
            '180.00'
        )

    # =========================================================
    # 02 - Update Athlete Profile
    # =========================================================

    def test_02_update_athlete_profile(self):

        self.login(self.athlete)

        response = self.client.patch(
            '/api/accounts/profile/',
            {
                'height': '185.00',
                'goal': 'weight_loss',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            str(self.profile.height),
            '185.00'
        )

        self.assertEqual(
            self.profile.goal,
            'weight_loss'
        )

    # =========================================================
    # 03 - Create Weight Record
    # =========================================================

    def test_03_create_weight_record(self):

        self.login(self.athlete)

        response = self.client.post(
            '/api/accounts/weights/',
            {
                'weight': '80.00',
                'date': '2026-08-19',
                'note': 'Morning weight',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WeightRecord.objects.filter(
                athlete=self.profile,
                weight='80.00'
            ).exists()
        )

    # =========================================================
    # 04 - List Weight Records
    # =========================================================

    def test_04_list_weight_records(self):

        WeightRecord.objects.create(
            athlete=self.profile,
            weight='80.00',
            date=date(2026, 8, 18)
        )

        WeightRecord.objects.create(
            athlete=self.profile,
            weight='79.50',
            date=date(2026, 8, 19)
        )

        self.login(self.athlete)

        response = self.client.get(
            '/api/accounts/weights/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

        # جدیدترین رکورد باید اول باشد
        self.assertEqual(
            response.data[0]['weight'],
            '79.50'
        )

    # =========================================================
    # 05 - Athlete Cannot Add Future Weight
    # =========================================================

    def test_05_cannot_add_future_weight(self):

        self.login(self.athlete)

        future_date = (
            date.today() +
            timedelta(days=1)
        )

        response = self.client.post(
            '/api/accounts/weights/',
            {
                'weight': '80.00',
                'date': str(future_date),
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # =========================================================
    # 06 - Cannot Add Invalid Weight
    # =========================================================

    def test_06_cannot_add_invalid_weight(self):

        self.login(self.athlete)

        response = self.client.post(
            '/api/accounts/weights/',
            {
                'weight': '-10',
                'date': str(date.today()),
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # =========================================================
    # 07 - Coach Cannot Add Weight
    # =========================================================

    def test_07_coach_cannot_add_weight(self):

        self.login(self.coach)

        response = self.client.post(
            '/api/accounts/weights/',
            {
                'weight': '80.00',
                'date': str(date.today()),
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 08 - BMI
    # =========================================================

    def test_08_bmi(self):

        WeightRecord.objects.create(
            athlete=self.profile,
            weight='81.00',
            date=date.today()
        )

        self.login(self.athlete)

        response = self.client.get(
            '/api/accounts/profile/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['bmi'],
            25.0
        )

        self.assertEqual(
            response.data['bmi_status'],
            'overweight'
        )