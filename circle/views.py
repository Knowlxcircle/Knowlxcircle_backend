import logging

from django.conf import settings
from django.db import IntegrityError
from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Circle, CircleMember, MemberSentiment
from .serializers import CircleSerializer, CircleMemberSerializer
from article.models import ArticleCircleAssociate, Articles

logger = logging.getLogger(__name__)

DEFAULT_SENTIMENT = "neutral"
DEFAULT_ROLE = "member"


def _server_error(detail=None):
    message = "Internal Server Error"
    if detail is not None and getattr(settings, "DEBUG", False):
        message = f"{message} : {detail}"
    return Response({
        "status": 500,
        "message": message,
        "response": None
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _bad_request(errors):
    return Response({
        "status": 400,
        "message": "Bad Request",
        "response": errors
    }, status=status.HTTP_400_BAD_REQUEST)


def _not_found(message="Not Found"):
    return Response({
        "status": 404,
        "message": message,
        "response": None
    }, status=status.HTTP_404_NOT_FOUND)


def _get_circle(circle_id):
    """Return the circle or None; never raises on a junk id."""
    try:
        return Circle.objects.get(id=circle_id)
    except (Circle.DoesNotExist, ValueError, TypeError):
        return None


def _get_or_create(manager, defaults=None, **lookup):
    """get_or_create that survives both the old world and the new one.

    MultipleObjectsReturned was the pre-constraint failure (duplicate rows the
    old code was free to create). IntegrityError is the one the new
    UniqueConstraints introduce: two concurrent requests can both miss the get
    and then race on the insert, and the loser must fall back to a read rather
    than 500.
    """
    try:
        return manager.get_or_create(defaults=defaults or {}, **lookup)
    except manager.model.MultipleObjectsReturned:
        return manager.filter(**lookup).order_by("id").first(), False
    except IntegrityError:
        existing = manager.filter(**lookup).order_by("id").first()
        if existing is None:
            raise
        return existing, False


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
            logger.exception("Failed to list circles")
            return _server_error(e)
            
class CreateCircle(APIView):
    def post(self, request):
        try:
            serializer = CircleSerializer(data=request.data)
            if not serializer.is_valid():
                return _bad_request(serializer.errors)
            circle = serializer.save()
            data = {}
            data["id"] = circle.id
            data["name"] = circle.name
            return Response({
                "status": 201,
                "message": "Created",
                "response": data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Failed to create circle")
            return _server_error(e)
        
class JoinCircle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            circle_id = request.data.get("circle_id")
            if circle_id in (None, ""):
                return _bad_request({"circle_id": "This field is required."})
            circle = _get_circle(circle_id)
            if circle is None:
                return _not_found()

            circle_member, created = _get_or_create(
                CircleMember.objects,
                defaults={"role": DEFAULT_ROLE},
                user=request.user,
                circle=circle
            )
            serializer = CircleMemberSerializer(circle_member)
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "circle_member": serializer.data,
                    "created": created
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to join circle")
            return _server_error(e)
            
class LeaveCircle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            circle_id = request.data.get("circle_id")
            if circle_id in (None, ""):
                return _bad_request({"circle_id": "This field is required."})
            circle = _get_circle(circle_id)
            if circle is None:
                return _not_found()

            try:
                circle_member = CircleMember.objects.get(user=request.user, circle=circle)
            except CircleMember.DoesNotExist:
                return _not_found("Not Found")

            # Serialize before deleting: the instance itself is not renderable.
            serializer = CircleMemberSerializer(circle_member)
            data = serializer.data
            circle_member.delete()
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "circle_member": data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to leave circle")
            return _server_error(e)
            
class GetCircle(APIView):
    def get(self, request, id):
        try:
            circle = _get_circle(id)
            if circle is None:
                return _not_found()
            serializer = CircleSerializer(circle).data
            serializer["article"] = []
            associations = ArticleCircleAssociate.objects.filter(circle=circle).select_related("article")
            for association in associations:
                serializer["article"].append({
                    "id": association.article.id,
                    "title": association.article.title,
                })
            return Response({
                "status": 200,
                "message": "Success",
                "response": serializer
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to fetch circle %s", id)
            return _server_error(e)
            
class GetAllCircle(APIView):
    def get(self, request):
        try:
            data = {}
            circles = list(Circle.objects.annotate(member_count=Count("members", distinct=True)))
            circle_ids = [circle.id for circle in circles]

            # Read-only: take the latest recorded sentiment, never create one.
            latest_sentiment = {}
            sentiments = MemberSentiment.objects.filter(circle_id__in=circle_ids).order_by(
                "circle_id", "-created_at", "-id"
            )
            for sentiment in sentiments:
                latest_sentiment.setdefault(sentiment.circle_id, sentiment.sentiment)

            data["circles"] = []
            for circle in circles:
                list_circle = {}
                list_circle["id"] = circle.id
                list_circle["name"] = circle.name
                list_circle["description"] = circle.description
                list_circle["members"] = circle.member_count
                list_circle["created_at"] = circle.created_at
                list_circle["updated_at"] = circle.updated_at
                list_circle["sentiment"] = latest_sentiment.get(circle.id) or DEFAULT_SENTIMENT
                data["circles"].append(list_circle)
                
            return Response({
                "status": 200,
                "message": "Success",
                "response": data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to list circles")
            return _server_error(e)

class GetCircleMembers(APIView):
    def get(self, request, id):
        try:
            circle = _get_circle(id)
            if circle is None:
                return _not_found()
            circle_members = CircleMember.objects.filter(circle=circle).select_related("user")
            serializer = CircleMemberSerializer(circle_members, many=True)
            return Response({
                "status": 200,
                "message": "Success",
                "response": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to list members of circle %s", id)
            return _server_error(e)
            
class AssociateCircle(APIView):
    def post(self, request):
        try:
            circle_id = request.data.get("circle_id")
            article_id = request.data.get("article_id")
            errors = {}
            if circle_id in (None, ""):
                errors["circle_id"] = "This field is required."
            if article_id in (None, ""):
                errors["article_id"] = "This field is required."
            if errors:
                return _bad_request(errors)

            circle = _get_circle(circle_id)
            if circle is None:
                return _not_found()
            try:
                article = Articles.objects.get(id=article_id)
            except (Articles.DoesNotExist, ValueError, TypeError):
                return _not_found()

            association, created = _get_or_create(
                ArticleCircleAssociate.objects,
                circle=circle,
                article=article
            )
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "id": association.id,
                    "circle_id": circle.id,
                    "article_id": article.id,
                    "created": created
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to associate article with circle")
            return _server_error(e)
