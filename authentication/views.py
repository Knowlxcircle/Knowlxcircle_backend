from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, SocialMedia
from .serializers import UserSerializer, SocialMediaSerializer

# Create your views here.
class Login(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = User.objects.get(username=username, password=password)
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "username": user.username,
                    "email": user.email,
                    "occupation": user.occupation,
                    "bio": user.bio
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Internal Server Error : {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        try:
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response({
                "status": 200,
                "message": "Success",
                "response": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Internal Server Error : {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SignUp(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            occupation = request.data.get('occupation')
            bio = request.data.get('bio')
            user = User.objects.create(username=username, password=password, email=email, occupation=occupation, bio=bio)
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "username": user.username,
                    "email": user.email,
                    "occupation": user.occupation,
                    "bio": user.bio
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Internal Server Error : {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    