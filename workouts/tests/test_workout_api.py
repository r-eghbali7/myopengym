from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from exercises.models import Exercise

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSet,
    WorkoutSession,
    WorkoutLog,
    WorkoutLogSet,
)


User = get_user_model()


class WorkoutAPITestCase(APITestCase):

    # =========================================================
    # SETUP
    # =========================================================

    def setUp(self):

        # -----------------------------------------------------
        # Athlete
        # -----------------------------------------------------

        self.user = User.objects.create_user(
            username='test_athlete',
            email='athlete@test.com',
            password='TestPassword123',
            role='athlete'
        )

        # -----------------------------------------------------
        # Coach
        # -----------------------------------------------------

        self.coach = User.objects.create_user(
            username='test_coach',
            email='coach@test.com',
            password='TestPassword123',
            role='coach'
        )

        # -----------------------------------------------------
        # Exercise
        # -----------------------------------------------------

        self.exercise = Exercise.objects.create(
            name='Test Bench Press',
            category='chest',
            target_muscle='chest'
        )

        # -----------------------------------------------------
        # Login Athlete
        # -----------------------------------------------------

        response = self.client.post(
            '/api/auth/token/',
            {
                'username': 'test_athlete',
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
    # HELPERS
    # =========================================================

    def create_plan(self):

        return WorkoutPlan.objects.create(
            name='Test Plan',
            description='Test workout plan',
            athlete=self.user,
            coach=self.coach,
            is_active=True
        )

    def create_day(self, plan=None):

        if plan is None:
            plan = self.create_plan()

        return WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1,
            name='Chest',
            description='Chest workout'
        )

    def create_workout_exercise(self, day=None):

        if day is None:
            day = self.create_day()

        return WorkoutExercise.objects.create(
            workout_day=day,
            exercise=self.exercise,
            order=1,
            notes=''
        )

    def create_session(self, day=None):

        if day is None:
            day = self.create_day()

        return WorkoutSession.objects.create(
            athlete=self.user,
            workout_day=day,
            is_completed=False
        )

    # =========================================================
    # 01 - LIST WORKOUT PLANS
    # =========================================================

    def test_01_list_workout_plans(self):

        WorkoutPlan.objects.create(
            name='Plan 1',
            athlete=self.user,
            coach=self.coach
        )

        WorkoutPlan.objects.create(
            name='Plan 2',
            athlete=self.user,
            coach=self.coach
        )

        response = self.client.get(
            '/api/workouts/'
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
    # 02 - CREATE WORKOUT DAY
    # =========================================================

    def test_02_create_workout_day(self):

        plan = self.create_plan()

        response = self.client.post(
            f'/api/workouts/{plan.id}/days/',
            {
                'day_number': 1,
                'name': 'سینه و پشت بازو',
                'description': 'روز اول',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WorkoutDay.objects.filter(
                workout_plan=plan,
                day_number=1
            ).exists()
        )

    # =========================================================
    # 03 - CREATE WORKOUT EXERCISE
    # =========================================================

    def test_03_create_workout_exercise(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1,
            name='Chest'
        )

        response = self.client.post(
            f'/api/workouts/days/{day.id}/exercises/',
            {
                'exercise': self.exercise.id,
                'order': 1,
                'notes': '',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WorkoutExercise.objects.filter(
                workout_day=day,
                exercise=self.exercise
            ).exists()
        )

    # =========================================================
    # 04 - CREATE WORKOUT SET
    # =========================================================

    def test_04_create_workout_set(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1
        )

        workout_exercise = WorkoutExercise.objects.create(
            workout_day=day,
            exercise=self.exercise,
            order=1
        )

        response = self.client.post(
            f'/api/workouts/exercises/{workout_exercise.id}/sets/',
            {
                'set_number': 1,
                'repetitions': 10,
                'weight': '60.00',
                'rest_seconds': 90,
                'notes': '',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WorkoutSet.objects.filter(
                workout_exercise=workout_exercise,
                set_number=1
            ).exists()
        )

    # =========================================================
    # 05 - START WORKOUT SESSION
    # =========================================================

    def test_05_start_session(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1,
            name='Chest'
        )

        response = self.client.post(
            f'/api/workouts/days/{day.id}/start/',
            {},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WorkoutSession.objects.filter(
                athlete=self.user,
                workout_day=day,
                is_completed=False
            ).exists()
        )

    # =========================================================
    # 06 - CREATE WORKOUT LOG
    # =========================================================

    def test_06_create_workout_log(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1
        )

        workout_exercise = WorkoutExercise.objects.create(
            workout_day=day,
            exercise=self.exercise,
            order=1
        )

        session = WorkoutSession.objects.create(
            athlete=self.user,
            workout_day=day,
            is_completed=False
        )

        response = self.client.post(
            f'/api/workouts/sessions/{session.id}/logs/',
            {
                'workout_exercise': workout_exercise.id,
                'notes': '',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WorkoutLog.objects.filter(
                session=session,
                workout_exercise=workout_exercise
            ).exists()
        )

    # =========================================================
    # 07 - CREATE WORKOUT LOG SET
    # =========================================================

    def test_07_create_workout_log_set(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1
        )

        workout_exercise = WorkoutExercise.objects.create(
            workout_day=day,
            exercise=self.exercise,
            order=1
        )

        session = WorkoutSession.objects.create(
            athlete=self.user,
            workout_day=day,
            is_completed=False
        )

        log = WorkoutLog.objects.create(
            session=session,
            workout_exercise=workout_exercise
        )

        response = self.client.post(
            f'/api/workouts/logs/{log.id}/sets/',
            {
                'set_number': 1,
                'repetitions': 10,
                'weight': '60.00',
                'rest_seconds': 90,
                'is_completed': True,
                'notes': '',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            WorkoutLogSet.objects.filter(
                workout_log=log,
                set_number=1
            ).exists()
        )

    # =========================================================
    # 08 - FINISH WORKOUT SESSION
    # =========================================================

    def test_08_finish_session(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1
        )

        session = WorkoutSession.objects.create(
            athlete=self.user,
            workout_day=day,
            is_completed=False
        )

        response = self.client.post(
            f'/api/workouts/sessions/{session.id}/finish/',
            {},
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
    # 09 - CANNOT ADD LOG AFTER FINISH
    # =========================================================

    def test_09_cannot_add_log_after_finish(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1
        )

        workout_exercise = WorkoutExercise.objects.create(
            workout_day=day,
            exercise=self.exercise,
            order=1
        )

        session = WorkoutSession.objects.create(
            athlete=self.user,
            workout_day=day,
            is_completed=True
        )

        response = self.client.post(
            f'/api/workouts/sessions/{session.id}/logs/',
            {
                'workout_exercise': workout_exercise.id,
                'notes': '',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 10 - CANNOT ADD SET AFTER FINISH
    # =========================================================

    def test_10_cannot_add_set_after_finish(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1
        )

        workout_exercise = WorkoutExercise.objects.create(
            workout_day=day,
            exercise=self.exercise,
            order=1
        )

        session = WorkoutSession.objects.create(
            athlete=self.user,
            workout_day=day,
            is_completed=True
        )

        log = WorkoutLog.objects.create(
            session=session,
            workout_exercise=workout_exercise
        )

        response = self.client.post(
            f'/api/workouts/logs/{log.id}/sets/',
            {
                'set_number': 1,
                'repetitions': 10,
                'weight': '60.00',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # 11 - LIST WORKOUT SESSIONS
    # =========================================================

    def test_11_list_sessions(self):

        plan = self.create_plan()

        day = WorkoutDay.objects.create(
            workout_plan=plan,
            day_number=1
        )

        WorkoutSession.objects.create(
            athlete=self.user,
            workout_day=day,
            is_completed=False
        )

        response = self.client.get(
            '/api/workouts/sessions/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )