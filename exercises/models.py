from django.db import models


class Exercise(models.Model):

    class Difficulty(models.TextChoices):
        BEGINNER = 'beginner', 'مبتدی'
        INTERMEDIATE = 'intermediate', 'متوسط'
        ADVANCED = 'advanced', 'پیشرفته'

    # ID from the original dataset
    external_id = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        max_length=255,
        unique=True
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )

    body_part = models.CharField(
        max_length=100,
        blank=True
    )

    equipment = models.CharField(
        max_length=100,
        blank=True
    )

    target_muscle = models.CharField(
        max_length=100,
        blank=True
    )

    muscle_group = models.CharField(
        max_length=100,
        blank=True
    )

    secondary_muscles = models.JSONField(
        default=list,
        blank=True
    )

    instructions = models.JSONField(
        default=dict,
        blank=True
    )

    instruction_steps = models.JSONField(
        default=dict,
        blank=True
    )

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER
    )

    media_id = models.CharField(
        max_length=100,
        blank=True
    )

    image = models.URLField(
        blank=True
    )

    gif_url = models.URLField(
        blank=True
    )

    attribution = models.CharField(
        max_length=255,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name