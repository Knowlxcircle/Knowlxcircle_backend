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