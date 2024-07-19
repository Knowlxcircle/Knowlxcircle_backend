from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Circle, CircleMember
from .serializers import CircleSerializer, CircleMemberSerializer

# Create your views here.
class HandleCircle(APIView):
    def get(self, request):
        try:
            circles = Circle.objects.all()
            serializer = CircleSerializer(circles, many=True)
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
            
class JoinCircle(APIView):
    def post(self, request):
        try:
            user = request.user
            circle_id = request.data.get("circle_id")
            circle = Circle.objects.get(id=circle_id)
            circle_member = CircleMember.objects.create(
                user=user,
                circle=circle
            )
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "circle_member": circle_member
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Internal Server Error : {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class LeaveCircle(APIView):
    def post(self, request):
        try:
            user = request.user
            circle_id = request.data.get("circle_id")
            circle = Circle.objects.get(id=circle_id)
            circle_member = CircleMember.objects.get(user=user, circle=circle)
            circle_member.delete()
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "circle_member": circle_member
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Internal Server Error : {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class GetCircle(APIView):
    def get(self, request):
        try:
            circle_id = request.data.get("circle_id")
            circle = Circle.objects.get(id=circle_id)
            serializer = CircleSerializer(circle)
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
            
class GetAllCircle(APIView):
    def get(self, request):
        try:
            circles = Circle.objects.all()
            serializer = CircleSerializer(circles, many=True)
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

class GetCircleMembers(APIView):
    def get(self, request):
        try:
            circle_id = request.data.get("circle_id")
            circle = Circle.objects.get(id=circle_id)
            circle_members = CircleMember.objects.filter(circle=circle)
            serializer = CircleMemberSerializer(circle_members, many=True)
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