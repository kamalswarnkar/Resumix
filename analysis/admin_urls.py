from django.urls import path
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from resumes.models import Resume
from .models import Analysis
from users.permissions import IsAdminRole
from users.serializers import UserListSerializer


class AdminViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def users(self, request):
        users = User.objects.all().order_by("-date_joined")
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def stats(self, request):
        total_users = User.objects.count()
        total_resumes = Resume.objects.count()
        total_analyses = Analysis.objects.count()
        avg_match = list(Analysis.objects.values_list("match_score", flat=True))
        avg_score = round(sum(avg_match) / len(avg_match), 2) if avg_match else 0.0

        return Response(
            {
                "total_users": total_users,
                "total_resumes": total_resumes,
                "total_analyses": total_analyses,
                "average_match_score": avg_score,
            },
            status=status.HTTP_200_OK,
        )


urlpatterns = [
    path("users/", AdminViewSet.as_view({"get": "users"}), name="admin-users"),
    path("stats/", AdminViewSet.as_view({"get": "stats"}), name="admin-stats"),
]
