from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserShortSerializer

User = get_user_model()


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserShortSerializer
