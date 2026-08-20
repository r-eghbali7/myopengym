from rest_framework import serializers

from .models import Exercise


class ExerciseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Exercise

        fields = [
            'id',
            'name',
            'slug',
            'category',
            'body_part',
            'equipment',
            'target_muscle',
            'muscle_group',
            'secondary_muscles',
            'difficulty',
            'instructions',
            'image',
            'gif_url',
        ]