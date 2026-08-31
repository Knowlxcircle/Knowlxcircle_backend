# myapp/views.py

import logging

from django.conf import settings
from rest_framework import generics
from .models import Member
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    MemberSerializer,
    MyTokenObtainPairSerializer,
    RegisterMemberSerializer,
    UserSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction

logger = logging.getLogger(__name__)


def _server_error(detail=None):
    message = "Internal Server Error"
    if detail is not None and getattr(settings, "DEBUG", False):
        message = f"{message} : {detail}"
    return Response(
        {
            "status": 500,
            "message": message,
            "response": None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def _bad_request(errors):
    return Response(
        {
            "status": 400,
            "message": "Bad Request",
            "response": errors
        }, status=status.HTTP_400_BAD_REQUEST
    )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            if not isinstance(username, str) or not isinstance(password, str):
                return _bad_request({"detail": "username and password are required"})
            username = username.strip()
            if not username or not password:
                return _bad_request({"detail": "username and password are required"})

            user = authenticate(request=request, username=username, password=password)
            if user is None:
                return Response(
                    {
                        "status": 401,
                        "message": "Unauthorized",
                        "response": None
                    }, status=status.HTTP_401_UNAUTHORIZED
                )

            # JWT is stateless: no session login, and no Member row is needed
            # because the token is derived from the User.
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    }
                }, status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.exception("Login failed")
            return _server_error(e)
            
class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            if not refresh:
                return _bad_request({"refresh": "This field is required."})

            try:
                token = RefreshToken(refresh)
            except TokenError:
                return _bad_request({"refresh": "Token is invalid or expired."})

            try:
                token.blacklist()
            except AttributeError:
                # token_blacklist is not installed: the client simply drops the
                # token, there is nothing to revoke server side.
                logger.warning("Token blacklist app is not installed; refresh token not revoked")

            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": None
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception("Logout failed")
            return _server_error(e)
            
class GetUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            users = User.objects.all().order_by("id")
            serializer = UserSerializer(users, many=True)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": {
                        "users": serializer.data
                    }
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception("Failed to list users")
            return _server_error(e)
            
class GetUserOneView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            try:
                user = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response(
                    {
                        "status": 404,
                        "message": "Not Found",
                        "response": None
                    }, status=status.HTTP_404_NOT_FOUND
                )
            serializer = UserSerializer(user)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": {
                        "user": serializer.data
                    }
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.exception("Failed to fetch user %s", id)
            return _server_error(e)
            
            
class RegisterMember(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = RegisterMemberSerializer(data=request.data)
            if not serializer.is_valid():
                return _bad_request(serializer.errors)

            data = serializer.validated_data
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=data["username"],
                        password=data["password"],
                        email=data.get("email") or ""
                    )
                    member = Member.objects.create(
                        user=user,
                        occupation=data.get("occupation") or "",
                        bio=data.get("bio") or ""
                    )
            except IntegrityError:
                # Nothing is committed: the atomic block rolled the User back.
                logger.warning("Duplicate registration for username %s", data["username"])
                return _bad_request({"username": "A user with that username already exists."})

            return Response(
                {
                    "status": 201,
                    "message": "Created",
                    "response": {
                        "user": UserSerializer(user).data,
                        "member": MemberSerializer(member).data
                    }
                }, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.exception("Member registration failed")
            return _server_error(e)
