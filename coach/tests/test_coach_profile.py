from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    CoachProfile,
)


User = get_user_model()


class CoachProfileTestCase(APITestCase):

    def setUp(self):

        # =====================================================
        # Coach
        # =====================================================

        self.coach = User.objects.create_user(
            username='profile_coach',
            email='profile_coach@test.com',
            password='TestPassword123',
            first_name='Ali',
            last_name='Ahmadi',
            role='coach'
        )

        self.profile = CoachProfile.objects.create(
            user=self.coach,
            bio='Experienced fitness coach',
            specialization='Bodybuilding',
            experience_years=5
        )

        # =====================================================
        # Athlete
        # =====================================================

        self.athlete = User.objects.create_user(
            username='profile_athlete',
            email='profile_athlete@test.com',
            password='TestPassword123',
            role='athlete'
        )

    # =========================================================
    # Login
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
    # 01 - Get Coach Profile
    # =========================================================

    def test_01_coach_can_get_profile(self):

        self.login(self.coach)

        response = self.client.get(
            '/api/coach/profile/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['bio'],
            'Experienced fitness coach'
        )

        self.assertEqual(
            response.data['specialization'],
            'Bodybuilding'
        )

        self.assertEqual(
            response.data['experience_years'],
            5
        )

        self.assertEqual(
            response.data['user']['username'],
            'profile_coach'
        )

    # =========================================================
    # 02 - Update Coach Profile
    # =========================================================

    def test_02_coach_can_update_profile(self):

        self.login(self.coach)

        response = self.client.patch(
            '/api/coach/profile/',
            {
                'bio': 'Professional bodybuilding coach',
                'specialization': 'Strength Training',
                'experience_years': 8,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.bio,
            'Professional bodybuilding coach'
        )

        self.assertEqual(
            self.profile.specialization,
            'Strength Training'
        )

        self.assertEqual(
            self.profile.experience_years,
            8
        )

    # =========================================================
    # 03 - Partial Update
    # =========================================================

    def test_03_coach_can_partially_update_profile(self):

        self.login(self.coach)

        response = self.client.patch(
            '/api/coach/profile/',
            {
                'bio': 'Updated bio',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.bio,
            'Updated bio'
        )

        self.assertEqual(
            self.profile.specialization,
            'Bodybuilding'
        )

        self.assertEqual(
            self.profile.experience_years,
            5
        )

    # =========================================================
    # 04 - Athlete Cannot Access Coach Profile
    # =========================================================

    def test_04_athlete_cannot_access_profile(self):

        self.login(self.athlete)

        response = self.client.get(
            '/api/coach/profile/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 05 - Athlete Cannot Update Coach Profile
    # =========================================================

    def test_05_athlete_cannot_update_profile(self):

        self.login(self.athlete)

        response = self.client.patch(
            '/api/coach/profile/',
            {
                'bio': 'Hacked bio',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 06 - Invalid Experience
    # =========================================================

    def test_06_invalid_experience(self):

        self.login(self.coach)

        response = self.client.patch(
            '/api/coach/profile/',
            {
                'experience_years': 101,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.experience_years,
            5
        )

    # =========================================================
    # 07 - Negative Experience
    # =========================================================

    def test_07_negative_experience(self):

        self.login(self.coach)

        response = self.client.patch(
            '/api/coach/profile/',
            {
                'experience_years': -1,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.experience_years,
            5
        )

    # =========================================================
    # 08 - Unauthenticated
    # =========================================================

    def test_08_unauthenticated(self):

        response = self.client.get(
            '/api/coach/profile/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )