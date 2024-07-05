from django.shortcuts import render
import google.generativeai as genai
from knowlxcirclebackend.settings import GOOGLE_API_KEY
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Prompt, GeminiResponse
from rest_framework import status
from .serializers import PromptSerializer, GeminiResponseSerializer


genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-pro")

class GenerateSearch(APIView):
    def post(self, request):
        try:
            data = {}
            search_query = request.data.get("search_query")
            prompt_response = model.generate_content(search_query)
            if(len(prompt_response.candidates) > 1):
                prompt_response = prompt_response.candidates[0]

            prompt = Prompt.objects.create(prompt=search_query)
            response_object = GeminiResponse.objects.create(prompt=prompt, response=prompt_response.text)
            # response_serializer = GeminiResponseSerializer(response_object)
            data["prompt"] = prompt.prompt
            data["response"] = prompt_response.text
            data["created_at"] = response_object.created_at
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        try:
            data = {}
            prompt = Prompt.objects.all().order_by("-created_at").first()
            response_object = GeminiResponse.objects.filter(prompt=prompt).first()
            prompt_serializer = PromptSerializer(prompt)
            data["prompt"] = prompt.prompt
            data["response"] = response_object.response
            data["created_at"] = response_object.created_at
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HomePage(APIView):
    def get(self, request):
        try:
            last_response = GeminiResponse.objects.all().order_by("-created_at").first()
            data = {}
            data["prompt"] = last_response.prompt.prompt
            data["response"] = last_response.response
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
        




