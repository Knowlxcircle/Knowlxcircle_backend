from django.shortcuts import render
from .models import Dashboard
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class HandleDashboard(APIView):
    def get(self, request):
        try:
            dashboards = Dashboard.objects.all()
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "dashboards": dashboards
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Internal Server Error : {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class GetDashboard(APIView):
    def get(self, request):
        try:
            pass
            
            
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Internal Server Error : {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)