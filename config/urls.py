from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/', include('api.urls')),

    path(
        'api/auth/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'api/auth/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path('api/accounts/', include('accounts.urls')),

    path('api/exercises/', include('exercises.urls')),

    path('api/workouts/', include('workouts.urls')),

    path(
        'api/coach/',
        include('coach.urls')
    ),

    path(
        'api/athlete/',
        include('athlete.urls')
    ),
]