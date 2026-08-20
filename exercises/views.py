from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Exercise
from .serializers import ExerciseSerializer

class ExerciseListView(
    generics.ListAPIView
):

    serializer_class = ExerciseSerializer
    permission_classes = [
        AllowAny
    ]

    def get_queryset(self):

        queryset = Exercise.objects.filter(
            is_active=True
        )

        search = self.request.query_params.get(
            'search'
        )

        category = self.request.query_params.get(
            'category'
        )

        body_part = self.request.query_params.get(
            'body_part'
        )

        equipment = self.request.query_params.get(
            'equipment'
        )

        difficulty = self.request.query_params.get(
            'difficulty'
        )

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )

        if category:
            queryset = queryset.filter(
                category__iexact=category
            )

        if body_part:
            queryset = queryset.filter(
                body_part__iexact=body_part
            )

        if equipment:
            queryset = queryset.filter(
                equipment__icontains=equipment
            )

        if difficulty:
            queryset = queryset.filter(
                difficulty__iexact=difficulty
            )

        return queryset.order_by('name')