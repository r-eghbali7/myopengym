from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from workouts.models import WorkoutPlan


User = get_user_model()


class WorkoutAssignmentTestCase(APITestCase):

    def setUp(self):

        # ==============================
        # Athlete
        # ==============================

        self.athlete = User.objects.create_user(
            username='assignment_athlete',
            email='assignment_athlete@test.com',
            password='TestPassword123',
            role='athlete'
        )


        # ==============================
        # Coach
        # ==============================

        self.coach = User.objects.create_user(
            username='assignment_coach',
            email='assignment_coach@test.com',
            password='TestPassword123',
            role='coach'
        )


    # ==============================
    # JWT Login
    # ==============================

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


    # =====================================================
    # Coach can create workout plan
    # =====================================================

    def test_coach_can_create_plan(self):

        self.login(
            self.coach
        )


        response = self.client.post(
            '/api/workouts/',
            {
                'name': 'Coach Plan',
                'description': 'Test Plan',
                'athlete': self.athlete.id,
                'is_active': True
            },
            format='json'
        )


        print(response.data)


        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )


        self.assertTrue(
            WorkoutPlan.objects.filter(
                athlete=self.athlete,
                coach=self.coach
            ).exists()
        )


    # =====================================================
    # Athlete cannot create workout plan
    # =====================================================

    def test_athlete_cannot_create_plan(self):

        self.login(
            self.athlete
        )


        response = self.client.post(
            '/api/workouts/',
            {
                'name': 'Unauthorized Plan',
                'description': 'Should fail',
                'athlete': self.athlete.id,
                'is_active': True
            },
            format='json'
        )


        print(response.data)


        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )