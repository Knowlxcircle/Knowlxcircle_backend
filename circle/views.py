from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Circle, CircleMember, MemberSentiment
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
            
class CreateCircle(APIView):
    def post(self, request):
        try:
            name = request.data.get("name")
            description = request.data.get("description")
            circle = Circle.objects.create(
                name=name,
                description=description
            )
            circle.save()
            data = {}
            data["id"] = circle.id
            data["name"] = circle.name
            return Response({
                "status": 200,
                "message": "Success",
                "response": data
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
            data = {}
            circles = Circle.objects.all()
            data["circles"] = []
            for circle in circles:
                list_circle = {}
                list_circle["id"] = circle.id
                list_circle["name"] = circle.name
                list_circle["description"] = circle.description
                
                circle_members = CircleMember.objects.filter(circle=circle)
                list_circle["members"] = len(circle_members)
                list_circle["created_at"] = circle.created_at
                list_circle["updated_at"] = circle.updated_at
                
                circle_sentiment, created = MemberSentiment.objects.get_or_create(circle=circle, sentiment="neutral", score=0.0)
                list_circle["sentiment"] = circle_sentiment.sentiment
                data["circles"].append(list_circle)
                
            return Response({
                "status": 200,
                "message": "Success",
                "response": data
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