import logging

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Prompt, GeminiResponse
from gemini.client import generate_text, LLMUnavailable

logger = logging.getLogger(__name__)

LLM_UNAVAILABLE_MESSAGE = "The AI service is unavailable right now. Please try again later."


def _envelope(http_status, message, payload=None):
    """Build the standard {status, message, response} envelope."""
    return Response(
        {
            "status": http_status,
            "message": message,
            "response": payload,
        }, status=http_status
    )


def _internal_error(exc, context):
    """Log the real exception and hand the client a generic message."""
    logger.exception("Internal server error in %s", context)
    message = "Internal Server Error"
    if settings.DEBUG:
        message = f"Internal Server Error : {exc}"
    return _envelope(status.HTTP_500_INTERNAL_SERVER_ERROR, message)


class GenerateSearch(APIView):

    def post(self, request):
        # A JSON body that is not an object has no .get(); guard before touching it.
        search_query = request.data.get("search_query") if isinstance(request.data, dict) else None
        search_query = "" if search_query is None else str(search_query).strip()
        if not search_query:
            return _envelope(status.HTTP_400_BAD_REQUEST, "search_query is required.")

        try:
            generated_text = generate_text(search_query)
        except LLMUnavailable:
            logger.warning("Gemini unavailable while generating a search response.")
            return _envelope(status.HTTP_503_SERVICE_UNAVAILABLE, LLM_UNAVAILABLE_MESSAGE)

        try:
            data = {}
            prompt = Prompt.objects.create(prompt=search_query)
            response_object = GeminiResponse.objects.create(prompt=prompt, response=generated_text)
            data["prompt"] = prompt.prompt
            data["response"] = response_object.response
            data["created_at"] = response_object.created_at
            return _envelope(status.HTTP_200_OK, "Success", data)
        except Exception as e:
            return _internal_error(e, "GenerateSearch.post")

    def get(self, request):
        try:
            data = {}
            prompt = Prompt.objects.order_by("-created_at").first()
            response_object = None
            if prompt is not None:
                response_object = GeminiResponse.objects.filter(prompt=prompt).order_by("-created_at").first()
            if prompt is None or response_object is None:
                return _envelope(status.HTTP_404_NOT_FOUND, "No generated response found.")

            data["prompt"] = prompt.prompt
            data["response"] = response_object.response
            data["created_at"] = response_object.created_at
            return _envelope(status.HTTP_200_OK, "Success", data)
        except Exception as e:
            return _internal_error(e, "GenerateSearch.get")


class HomePage(APIView):
    def get(self, request):
        try:
            last_response = (
                GeminiResponse.objects.select_related("prompt").order_by("-created_at").first()
            )
            if last_response is None:
                return _envelope(status.HTTP_404_NOT_FOUND, "No generated response found.")

            data = {}
            data["prompt"] = last_response.prompt.prompt
            data["response"] = last_response.response
            return _envelope(status.HTTP_200_OK, "Success", data)
        except Exception as e:
            return _internal_error(e, "HomePage.get")


class ChatPage(APIView):
    def get(self, request):
        try:
            responses = GeminiResponse.objects.select_related("prompt").order_by("-created_at")
            data = [
                {
                    "id": res.id,
                    "prompt": res.prompt.prompt,
                    "response": res.response,
                    "created_at": res.created_at,
                }
                for res in responses
            ]
            return _envelope(status.HTTP_200_OK, "Success", data)
        except Exception as e:
            return _internal_error(e, "ChatPage.get")

    def post(self, request):
        # A JSON body that is not an object has no .get(); guard before touching it.
        chat_query = request.data.get("chat_query") if isinstance(request.data, dict) else None
        chat_query = "" if chat_query is None else str(chat_query).strip()
        if not chat_query:
            return _envelope(status.HTTP_400_BAD_REQUEST, "chat_query is required.")

        try:
            generated_text = generate_text(chat_query)
        except LLMUnavailable:
            logger.warning("Gemini unavailable while answering a chat query.")
            return _envelope(status.HTTP_503_SERVICE_UNAVAILABLE, LLM_UNAVAILABLE_MESSAGE)

        try:
            data = {}
            prompt = Prompt.objects.create(prompt=chat_query)
            gemini_response = GeminiResponse.objects.create(prompt=prompt, response=generated_text)
            data["id"] = gemini_response.id
            data["prompt"] = prompt.prompt
            data["response"] = gemini_response.response
            data["created_at"] = gemini_response.created_at
            return _envelope(status.HTTP_201_CREATED, "Created", data)
        except Exception as e:
            return _internal_error(e, "ChatPage.post")


class ChatPageDetail(APIView):
    def get(self, request, id):
        try:
            data = {}
            response_object = GeminiResponse.objects.select_related("prompt").get(id=id)
            data["prompt"] = response_object.prompt.prompt
            data["response"] = response_object.response
            data["created_at"] = response_object.created_at
            return _envelope(status.HTTP_200_OK, "Success", data)
        except GeminiResponse.DoesNotExist:
            return _envelope(status.HTTP_404_NOT_FOUND, "Chat response not found.")
        except Exception as e:
            return _internal_error(e, "ChatPageDetail.get")
