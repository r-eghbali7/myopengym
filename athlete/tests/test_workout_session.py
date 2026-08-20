
from decimal import Decimal

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    User,
    AthleteProfile,
)

from exercises.models import Exercise

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSession,
)


class AthleteWorkoutSessionTests(
    APITestCase
):

    def setUp(self):

        # =====================================================
        # Athlete
        # =====================================================

        self.athlete = User.objects.create_user(
            username='athlete',
            email='athlete@test.com',
            password='12345678',
            role='athlete',
        )

        self.athlete_profile = (
            AthleteProfile.objects.create(
                user=self.athlete,
                gender='male',
                height=180,
                goal='muscle_gain',
                activity_level='moderate',
            )
        )

        # =====================================================
        # Other Athlete
        # =====================================================

        self.other_athlete = User.objects.create_user(
            username='other_athlete',
            email='other@test.com',
            password='12345678',
            role='athlete',
        )

        self.other_athlete_profile = (
            AthleteProfile.objects.create(
                user=self.other_athlete,
                gender='male',
                height=175,
                goal='weight_loss',
                activity_level='light',
            )
        )

        # =====================================================
        # Coach
        # =====================================================

        self.coach = User.objects.create_user(
            username='coach',
            email='coach@test.com',
            password='12345678',
            role='coach',
        )

        # =====================================================
        # Exercise
        # =====================================================

        self.exercise = Exercise.objects.create(
            external_id='session-test-001',
            name='Bench Press',
            slug='bench-press-session-test',
            category='strength',
            body_part='chest',
            equipment='barbell',
            target_muscle='chest',
            muscle_group='chest',
        )

        # =====================================================
        # Athlete Workout Plan
        # =====================================================

        self.plan = WorkoutPlan.objects.create(
            name='Athlete Workout',
            description='Session test plan',
            athlete=self.athlete,
            coach=self.coach,
            is_active=True,
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

        self.workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=self.day,
                exercise=self.exercise,
                order=1,
            )
        )

        # =====================================================
        # Other Athlete Plan
        # =====================================================

        self.other_plan = WorkoutPlan.objects.create(
            name='Other Athlete Plan',
            description='Other plan',
            athlete=self.other_athlete,
            coach=self.coach,
            is_active=True,
        )

        self.other_day = WorkoutDay.objects.create(
            workout_plan=self.other_plan,
            day_number=1,
            name='Other Day',
        )

        # =====================================================
        # Authentication
        # =====================================================

        self.client.force_authenticate(
            user=self.athlete
        )

        # =====================================================
        # URLs
        # =====================================================

        self.sessions_url = reverse(
            'athlete-workout-session-list-create'
        )

    # =========================================================
    # Create Session
    # =========================================================

    def test_create_workout_session(self):

        response = self.client.post(
            self.sessions_url,
            {
                'workout_day': self.day.id,
                'notes': 'Starting workout',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['workout_day'],
            self.day.id
        )

        self.assertEqual(
            response.data['athlete'],
            self.athlete.id
        )

        self.assertFalse(
            response.data['is_completed']
        )

        self.assertIsNotNone(
            response.data['started_at']
        )

    # =========================================================
    # Athlete Automatically Assigned
    # =========================================================

    def test_session_athlete_is_request_user(self):

        response = self.client.post(
            self.sessions_url,
            {
                'workout_day': self.day.id,
                'athlete': self.other_athlete.id,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        session = WorkoutSession.objects.get(
            id=response.data['id']
        )

        self.assertEqual(
            session.athlete,
            self.athlete
        )

    # =========================================================
    # Cannot Create Session For Another Athlete
    # =========================================================

    def test_cannot_create_session_for_another_athlete(self):

        response = self.client.post(
            self.sessions_url,
            {
                'workout_day': self.other_day.id,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            'workout_day',
            response.data
        )

    # =========================================================
    # List Sessions
    # =========================================================

    def test_list_workout_sessions(self):

        WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
            notes='Session 1',
        )

        WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
            notes='Session 2',
        )

        response = self.client.get(
            self.sessions_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

    # =========================================================
    # Cannot See Another Athlete Sessions
    # =========================================================

    def test_athlete_can_only_see_own_sessions(self):

        WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
        )

        WorkoutSession.objects.create(
            athlete=self.other_athlete,
            workout_day=self.other_day,
        )

        response = self.client.get(
            self.sessions_url
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
            response.data[0]['athlete'],
            self.athlete.id
        )

    # =========================================================
    # Get Session Detail
    # =========================================================

    def test_get_session_detail(self):

        session = WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
            notes='My session',
        )

        url = reverse(
            'athlete-workout-session-detail',
            kwargs={
                'session_id': session.id
            }
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            session.id
        )

    # =========================================================
    # Cannot Access Another Athlete Session
    # =========================================================

    def test_cannot_access_another_athlete_session(self):

        session = WorkoutSession.objects.create(
            athlete=self.other_athlete,
            workout_day=self.other_day,
        )

        url = reverse(
            'athlete-workout-session-detail',
            kwargs={
                'session_id': session.id
            }
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # =========================================================
    # Complete Session
    # =========================================================

    def test_complete_workout_session(self):

        session = WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
            is_completed=False,
        )

        url = reverse(
            'athlete-workout-session-detail',
            kwargs={
                'session_id': session.id
            }
        )

        response = self.client.patch(
            url,
            {
                'is_completed': True,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        session.refresh_from_db()

        self.assertTrue(
            session.is_completed
        )

        self.assertIsNotNone(
            session.finished_at
        )

    # =========================================================
    # Session Notes
    # =========================================================

    def test_update_session_notes(self):

        session = WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
            notes='Old notes',
        )

        url = reverse(
            'athlete-workout-session-detail',
            kwargs={
                'session_id': session.id
            }
        )

        response = self.client.patch(
            url,
            {
                'notes': 'New notes',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        session.refresh_from_db()

        self.assertEqual(
            session.notes,
            'New notes'
        )

    # =========================================================
    # Completed Session Cannot Become Active
    # =========================================================

    def test_completed_session_cannot_be_reopened(self):

        session = WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
            is_completed=True,
        )

        url = reverse(
            'athlete-workout-session-detail',
            kwargs={
                'session_id': session.id
            }
        )

        response = self.client.patch(
            url,
            {
                'is_completed': False,
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # =========================================================
    # Unauthenticated
    # =========================================================

    def test_unauthenticated_cannot_access_sessions(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.sessions_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # =========================================================
    # Coach Cannot Use Athlete API
    # =========================================================

    def test_coach_cannot_access_athlete_sessions(self):

        self.client.force_authenticate(
            user=self.coach
        )

        response = self.client.get(
            self.sessions_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            0
        )
