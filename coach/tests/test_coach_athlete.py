
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import (
    User,
    AthleteProfile,
    WeightRecord,
)

from exercises.models import Exercise

from workouts.models import (
    WorkoutPlan,
    WorkoutDay,
    WorkoutExercise,
    WorkoutSession,
    WorkoutLog,
    WorkoutLogSet,
)


class CoachAthleteTests(APITestCase):

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
        # Athlete 1
        # =====================================================

        self.athlete = User.objects.create_user(
            username='athlete',
            email='athlete@test.com',
            password='12345678',
            role='athlete',
            first_name='Ali',
            last_name='Ahmadi',
        )

        self.athlete_profile = AthleteProfile.objects.create(
            user=self.athlete,
            gender='male',
            height=180,
            goal='muscle_gain',
            activity_level='moderate',
        )

        # =====================================================
        # Athlete 2
        # =====================================================

        self.other_athlete = User.objects.create_user(
            username='other_athlete',
            email='otherathlete@test.com',
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
        # Weight Records
        # =====================================================

        WeightRecord.objects.create(
            athlete=self.athlete_profile,
            weight=Decimal('80.00'),
            date='2026-01-01',
        )

        WeightRecord.objects.create(
            athlete=self.athlete_profile,
            weight=Decimal('78.00'),
            date='2026-02-01',
        )

        WeightRecord.objects.create(
            athlete=self.athlete_profile,
            weight=Decimal('76.00'),
            date='2026-03-01',
        )

        # =====================================================
        # Exercise
        # =====================================================

        self.exercise = Exercise.objects.create(
            external_id='athlete-test-001',
            name='Bench Press',
            slug='bench-press-athlete-test',
            category='strength',
            body_part='chest',
            equipment='barbell',
            target_muscle='chest',
            muscle_group='chest',
        )

        # =====================================================
        # Coach 1 Plan
        # =====================================================

        self.plan = WorkoutPlan.objects.create(
            name='Ali Workout Plan',
            description='Main workout plan',
            athlete=self.athlete,
            coach=self.coach,
            is_active=True,
            start_date='2026-01-01',
            end_date='2026-03-31',
        )

        # =====================================================
        # Plan 2
        # =====================================================

        self.second_plan = WorkoutPlan.objects.create(
            name='Ali Second Plan',
            description='Second workout plan',
            athlete=self.athlete,
            coach=self.coach,
            is_active=False,
        )

        # =====================================================
        # Other Coach Plan
        # =====================================================

        self.other_plan = WorkoutPlan.objects.create(
            name='Other Coach Plan',
            description='Other coach plan',
            athlete=self.other_athlete,
            coach=self.other_coach,
            is_active=True,
        )

        # =====================================================
        # Workout Days
        # =====================================================

        self.day = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=1,
            name='Chest Day',
            description='Chest workout',
        )

        self.second_day = WorkoutDay.objects.create(
            workout_plan=self.plan,
            day_number=2,
            name='Back Day',
            description='Back workout',
        )

        self.second_plan_day = WorkoutDay.objects.create(
            workout_plan=self.second_plan,
            day_number=1,
            name='Leg Day',
        )

        self.other_plan_day = WorkoutDay.objects.create(
            workout_plan=self.other_plan,
            day_number=1,
            name='Other Coach Day',
        )

        # =====================================================
        # Workout Exercises
        # =====================================================

        self.workout_exercise = WorkoutExercise.objects.create(
            workout_day=self.day,
            exercise=self.exercise,
            order=1,
        )

        self.second_workout_exercise = (
            WorkoutExercise.objects.create(
                workout_day=self.second_day,
                exercise=self.exercise,
                order=1,
            )
        )

        WorkoutExercise.objects.create(
            workout_day=self.second_plan_day,
            exercise=self.exercise,
            order=1,
        )

        WorkoutExercise.objects.create(
            workout_day=self.other_plan_day,
            exercise=self.exercise,
            order=1,
        )

        # =====================================================
        # Sessions
        # =====================================================

        self.completed_session = WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.day,
            is_completed=True,
            notes='Completed workout',
        )

        self.completed_session.finished_at = (
            self.completed_session.started_at
        )

        self.completed_session.save(
            update_fields=['finished_at']
        )

        self.pending_session = WorkoutSession.objects.create(
            athlete=self.athlete,
            workout_day=self.second_day,
            is_completed=False,
            notes='Pending workout',
        )

        # =====================================================
        # Workout Log
        # =====================================================

        self.workout_log = WorkoutLog.objects.create(
            session=self.completed_session,
            workout_exercise=self.workout_exercise,
            notes='Good workout',
        )

        # =====================================================
        # Workout Log Sets
        # =====================================================

        WorkoutLogSet.objects.create(
            workout_log=self.workout_log,
            set_number=1,
            repetitions=10,
            weight=Decimal('50.00'),
            rest_seconds=90,
            is_completed=True,
        )

        WorkoutLogSet.objects.create(
            workout_log=self.workout_log,
            set_number=2,
            repetitions=8,
            weight=Decimal('60.00'),
            rest_seconds=90,
            is_completed=True,
        )

        # =====================================================
        # Authentication
        # =====================================================

        self.client.force_authenticate(
            user=self.coach
        )

        # =====================================================
        # URLs
        # =====================================================

        self.athletes_url = reverse(
            'coach-athletes'
        )

        self.athlete_detail_url = reverse(
            'coach-athlete-detail',
            kwargs={
                'athlete_id': self.athlete.id
            }
        )

        self.progress_url = reverse(
            'coach-athlete-progress',
            kwargs={
                'athlete_id': self.athlete.id
            }
        )

        self.workouts_url = reverse(
            'coach-athlete-workouts',
            kwargs={
                'athlete_id': self.athlete.id
            }
        )

    # =========================================================
    # Athlete List
    # =========================================================

    def test_list_coach_athletes(self):

        response = self.client.get(
            self.athletes_url
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
            self.athlete_profile.id
        )

    # =========================================================
    # Athlete List - Current Weight
    # =========================================================

    def test_list_athlete_current_weight(self):

        response = self.client.get(
            self.athletes_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data[0]['current_weight'],
            '76.00'
        )

    # =========================================================
    # Athlete List - Goal
    # =========================================================

    def test_list_athlete_goal(self):

        response = self.client.get(
            self.athletes_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data[0]['goal'],
            self.athlete_profile.goal
        )

    # =========================================================
    # Athlete Detail
    # =========================================================

    def test_get_athlete_detail(self):

        response = self.client.get(
            self.athlete_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['id'],
            self.athlete_profile.id
        )

        self.assertEqual(
            response.data['user']['id'],
            self.athlete.id
        )

        self.assertEqual(
            response.data['user']['username'],
            'athlete'
        )

    # =========================================================
    # Athlete Detail - Weight
    # =========================================================

    def test_athlete_detail_weight_data(self):

        response = self.client.get(
            self.athlete_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['current_weight'],
            '76.00'
        )

        self.assertEqual(
            response.data['starting_weight'],
            '80.00'
        )

        self.assertEqual(
            response.data['weight_change'],
            '-4.00'
        )

    # =========================================================
    # Athlete Detail - BMI
    # =========================================================

    def test_athlete_detail_bmi(self):

        response = self.client.get(
            self.athlete_detail_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIsNotNone(
            response.data['bmi']
        )

        self.assertIsNotNone(
            response.data['bmi_status']
        )

    # =========================================================
    # Athlete Detail - Other Coach
    # =========================================================

    def test_coach_cannot_access_another_coach_athlete(self):

        url = reverse(
            'coach-athlete-detail',
            kwargs={
                'athlete_id': self.other_athlete.id
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
    # Athlete Progress
    # =========================================================

    def test_get_athlete_progress(self):

        response = self.client.get(
            self.progress_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['total_plans'],
            2
        )

        self.assertEqual(
            response.data['active_plans'],
            1
        )

        self.assertEqual(
            response.data['total_days'],
            3
        )

        self.assertEqual(
            response.data['total_exercises'],
            3
        )

        self.assertEqual(
            response.data['total_sessions'],
            2
        )

        self.assertEqual(
            response.data['completed_sessions'],
            1
        )

    # =========================================================
    # Progress Completion Rate
    # =========================================================

    def test_athlete_progress_completion_rate(self):

        response = self.client.get(
            self.progress_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['completion_rate'],
            50.0
        )

    # =========================================================
    # Progress Volume
    # =========================================================

    def test_athlete_progress_total_volume(self):

        response = self.client.get(
            self.progress_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # 10 * 50 + 8 * 60 = 980
        self.assertEqual(
            Decimal(
                str(response.data['total_volume'])
            ),
            Decimal('980.00')
        )

    # =========================================================
    # Progress Weight
    # =========================================================

    def test_athlete_progress_weight(self):

        response = self.client.get(
            self.progress_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['current_weight'],
            '76.00'
        )

        self.assertEqual(
            response.data['starting_weight'],
            '80.00'
        )

        self.assertEqual(
            response.data['weight_change'],
            '-4.00'
        )

    # =========================================================
    # Progress - Other Coach
    # =========================================================

    def test_coach_cannot_access_another_coach_progress(self):

        url = reverse(
            'coach-athlete-progress',
            kwargs={
                'athlete_id': self.other_athlete.id
            }
        )

        response = self.client.get(
            url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    # =========================================================
    # Athlete Workouts
    # =========================================================

    def test_list_athlete_workouts(self):

        response = self.client.get(
            self.workouts_url
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
    # Athlete Workouts - Correct Plans
    # =========================================================

    def test_athlete_workouts_belong_to_coach(self):

        response = self.client.get(
            self.workouts_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        plan_names = [
            item['name']
            for item in response.data
        ]

        self.assertIn(
            'Ali Workout Plan',
            plan_names
        )

        self.assertIn(
            'Ali Second Plan',
            plan_names
        )

        self.assertNotIn(
            'Other Coach Plan',
            plan_names
        )

    # =========================================================
    # Athlete Workouts - Statistics
    # =========================================================

    def test_athlete_workout_statistics(self):

        response = self.client.get(
            self.workouts_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        plan = next(
            item
            for item in response.data
            if item['name'] == 'Ali Workout Plan'
        )

        self.assertEqual(
            plan['total_days'],
            2
        )

        self.assertEqual(
            plan['total_exercises'],
            2
        )

        self.assertEqual(
            plan['total_sessions'],
            2
        )

        self.assertEqual(
            plan['completed_sessions'],
            1
        )

    # =========================================================
    # Athlete Workouts - Other Athlete
    # =========================================================

    def test_coach_cannot_list_another_coach_athlete_workouts(
        self
    ):

        url = reverse(
            'coach-athlete-workouts',
            kwargs={
                'athlete_id': self.other_athlete.id
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
            len(response.data),
            0
        )

    # =========================================================
    # Unauthenticated
    # =========================================================

    def test_unauthenticated_user_cannot_access_athletes(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            self.athletes_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    # =========================================================
    # Non Coach
    # =========================================================

    def test_athlete_cannot_access_coach_athletes(self):

        self.client.force_authenticate(
            user=self.athlete
        )

        response = self.client.get(
            self.athletes_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )
