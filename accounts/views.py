from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    LogoutSerializer,
    ProfileSerializer,
    RegisterSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.status_code = status.HTTP_200_OK
        return response


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data={}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Chiqildi'})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        token = serializer.save()
        return Response({'token': token.key})
