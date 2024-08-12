# myapp/views.py

from rest_framework import generics
from .models import Member, SocialMedia
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            user = authenticate(username=username, password=password)
            if user is None:
                return Response(
                    {
                        "status": 401,
                        "message": "Unauthorized"
                    }, status=status.HTTP_401_UNAUTHORIZED
                )
            member = Member.objects.get(user=user)
            login(request, user)

            refresh = RefreshToken.for_user(member.user)
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
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            token = RefreshToken(refresh)
            
            token.blacklist()
            logout(request)
            return Response(
                {
                    "status": 200,
                    "message": "Success"
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class GetUserView(APIView):
    def get(self, request):
        try:
            user = User.objects.all()
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": {
                        "users": user
                    }
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class GetUserOneView(APIView):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": {
                        "user": user
                    }
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            
class RegisterMember(APIView):
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")
            email = request.data.get("email")
            occupation = request.data.get("occupation")
            bio = request.data.get("bio")
            user = User.objects.create_user(username=username, password=password, email=email)
            member = Member.objects.create(user=user, occupation=occupation, bio=bio)
            user.save()
            member.save()
            return Response(
                {
                    "status": 201,
                    "message": "Created",
                    "response": {
                        "user": user,
                        "member": member
                    }
                }, status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )