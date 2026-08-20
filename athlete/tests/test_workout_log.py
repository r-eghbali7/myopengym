
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from exercises.models import Exercise

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSession,
    WorkoutLog,
)


class AthleteWorkoutLogTests(APITestCase):

    def setUp(self):

        # =================================================
        # Users
        # =================================================

        self.athlete = User.objects.create_user(
            username='athlete1',
            email='athlete@test.com',
            password='password123',
            role='athlete',
        )

        self.other_athlete = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='password123',
            role='athlete',
        )

        self.coach = User.objects.create_user(
            username='coach1',
            email='coach@test.com',
            password='password123',
            role='coach',
        )

        # =================================================
        # Exercises
        # =================================================

        self.exercise = Exercise.objects.create(
            external_id='exercise-1',
            name='Bench Press',
            slug='bench-press',
        )

        self.exercise_2 = Exercise.objects.create(
            external_id='exercise-2',
            name='Squat',
            slug='squat',
        )

        # =================================================
        # Athlete Workout Plan
        # =================================================

        self.plan = WorkoutPlan.objects.create(
            name='Athlete Plan',
            athlete=self.athlete,
            coach=self.coach,
        )

        self.day = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=1,
            name='Chest Day',
        )

        self.workout_exercise = WorkoutExercise.objects.create(
            workout_day=self.day,
            exercise=self.exercise,
            order=1,
        )

        self.workout_exercise_2 = WorkoutExercise.objects.create(
            workout_day=self.day,
            exercise=self.exercise_2,
            order=2,
        )

        # =================================================
        # Other Athlete Plan
        # =================================================

        self.other_plan = WorkoutPlan.objects.create(
            name='Other Athlete Plan',
            athlete=self.other_athlete,
            coach=self.coach,
        )

        self.other_day = WorkoutDay.objects.create(
            workout_plan=self.other_plan,
            day_number=1,
            name='Other Day',
        )

        self.other_workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=self.other_day,
                exercise=self.exercise,
                order=1,
            )
        )

        # =================================================
        # Another Day For Same Athlete
        # =================================================

        self.another_day = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=2,
            name='Leg Day',
        )

        self.another_workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=self.another_day,
                exercise=self.exercise_2,
                order=1,
            )
        )

        # =================================================
        # Sessions
        # =================================================

        self.session = WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
        )

        self.other_session = WorkoutSession.objects.create(
            athlete=self.other_athlete,
            workout_day=self.other_day,
        )

        # =================================================
        # URLs
        # =================================================

        self.logs_url = reverse(
            'athlete-workout-log-list-create',
            kwargs={
                'session_id': self.session.id,
            },
        )

    # =====================================================
    # Authentication
    # =====================================================

    def test_unauthenticated_cannot_access_logs(self):

        response = self.client.get(
            self.logs_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # =====================================================
    # Create
    # =====================================================

    def test_create_workout_log(self):

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.post(
            self.logs_url,
            {
                'workout_exercise': self.workout_exercise.id,
                'notes': 'Good set',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            WorkoutLog.objects.count(),
            1,
        )

        log = WorkoutLog.objects.first()

        self.assertEqual(
            log.session,
            self.session,
        )

        self.assertEqual(
            log.workout_exercise,
            self.workout_exercise,
        )

        self.assertEqual(
            log.notes,
            'Good set',
        )

    # =====================================================
    # Create Without Exercise
    # =====================================================

    def test_create_log_without_workout_exercise(self):

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.post(
            self.logs_url,
            {
                'notes': 'No exercise',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================================
    # Session Ownership
    # =====================================================

    def test_cannot_access_another_athlete_session(self):

        self.client.force_authenticate(
            user=self.athlete
        )

        url = reverse(
            'athlete-workout-log-list-create',
            kwargs={
                'session_id': self.other_session.id,
            },
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =====================================================
    # Cannot Create Log For Another Athlete
    # =====================================================

    def test_cannot_create_log_for_another_athlete(self):

        self.client.force_authenticate(
            user=self.athlete
        )

        url = reverse(
            'athlete-workout-log-list-create',
            kwargs={
                'session_id': self.other_session.id,
            },
        )

        response = self.client.post(
            url,
            {
                'workout_exercise': (
                    self.other_workout_exercise.id
                ),
                'notes': 'Invalid',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =====================================================
    # Exercise From Another Athlete
    # =====================================================

    def test_cannot_log_exercise_from_another_athlete(
        self,
    ):

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.post(
            self.logs_url,
            {
                'workout_exercise': (
                    self.other_workout_exercise.id
                ),
                'notes': 'Invalid exercise',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================================
    # Exercise Must Belong To Session Day
    # =====================================================

    def test_exercise_must_belong_to_session_day(
        self,
    ):

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.post(
            self.logs_url,
            {
                'workout_exercise': (
                    self.another_workout_exercise.id
                ),
                'notes': 'Wrong day',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================================
    # List Own Logs
    # =====================================================

    def test_list_workout_logs(self):

        WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
            notes='First log',
        )

        WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise_2,
            notes='Second log',
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.get(
            self.logs_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            2,
        )

    # =====================================================
    # Only Own Logs
    # =====================================================

    def test_athlete_can_only_see_own_logs(self):

        WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
        )

        WorkoutLog.objects.create(
            session=self.other_session,
            workout_exercise=self.other_workout_exercise,
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.get(
            self.logs_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

        self.assertEqual(
            response.data[0]['session_id'],
            self.session.id,
        )

    # =====================================================
    # Duplicate Exercise In Session
    # =====================================================

    def test_duplicate_workout_log_not_allowed(self):

        WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.post(
            self.logs_url,
            {
                'workout_exercise': (
                    self.workout_exercise.id
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================================
    # Get Detail
    # =====================================================

    def test_get_workout_log_detail(self):

        log = WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
            notes='Test log',
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['id'],
            log.id,
        )

        self.assertEqual(
            response.data['session_id'],
            self.session.id,
        )

        self.assertEqual(
            response.data['exercise_name'],
            self.exercise.name,
        )

    # =====================================================
    # Cannot Access Another Athlete Log
    # =====================================================

    def test_cannot_access_another_athlete_log(self):

        log = WorkoutLog.objects.create(
            session=self.other_session,
            workout_exercise=self.other_workout_exercise,
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =====================================================
    # Update Notes
    # =====================================================

    def test_update_workout_log_notes(self):

        log = WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
            notes='Old note',
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.patch(
            url,
            {
                'notes': 'Updated note',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        log.refresh_from_db()

        self.assertEqual(
            log.notes,
            'Updated note',
        )

    # =====================================================
    # Update Cannot Change Session
    # =====================================================

    def test_cannot_change_session(self):

        log = WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.patch(
            url,
            {
                'session': self.other_session.id,
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        log.refresh_from_db()

        self.assertEqual(
            log.session,
            self.session,
        )

    # =====================================================
    # Update Cannot Change Exercise To Wrong Day
    # =====================================================

    def test_cannot_change_exercise_to_wrong_day(self):

        log = WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.patch(
            url,
            {
                'workout_exercise': (
                    self.another_workout_exercise.id
                ),
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        log.refresh_from_db()

        self.assertEqual(
            log.workout_exercise,
            self.workout_exercise,
        )

    # =====================================================
    # Update Same Exercise Is Allowed
    # =====================================================

    def test_update_notes_without_changing_exercise(self):

        log = WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
            notes='Old note',
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.patch(
            url,
            {
                'workout_exercise': (
                    self.workout_exercise.id
                ),
                'notes': 'New note',
            },
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        log.refresh_from_db()

        self.assertEqual(
            log.workout_exercise,
            self.workout_exercise,
        )

        self.assertEqual(
            log.notes,
            'New note',
        )

    # =====================================================
    # Delete
    # =====================================================

    def test_delete_workout_log(self):

        log = WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.delete(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            WorkoutLog.objects.filter(
                id=log.id
            ).exists()
        )

    # =====================================================
    # Coach Cannot Access
    # =====================================================

    def test_coach_cannot_access_athlete_logs(self):

        self.client.force_authenticate(
            user=self.coach
        )

        response = self.client.get(
            self.logs_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =====================================================
    # Coach Cannot Access Log Detail
    # =====================================================

    def test_coach_cannot_access_log_detail(self):

        log = WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        self.client.force_authenticate(
            user=self.coach
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # =====================================================
    # Unauthenticated Detail
    # =====================================================

    def test_unauthenticated_cannot_access_log_detail(
        self,
    ):

        log = WorkoutLog.objects.create(
            session=self.session,
            workout_exercise=self.workout_exercise,
        )

        url = reverse(
            'athlete-workout-log-detail',
            kwargs={
                'log_id': log.id,
            },
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
