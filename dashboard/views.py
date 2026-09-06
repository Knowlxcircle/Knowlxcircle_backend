import logging
import os
import statistics
from collections import Counter

from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from article.models import Articles, ArticleSentiment, ArticleStamp, Section
from gemini.client import LLMUnavailable, generate_text

from .models import Dashboard
from .serializers import DashboardSerializer

logger = logging.getLogger(__name__)

# Cache key for the aggregated dashboard payload. Bump the suffix whenever the
# payload shape changes so stale entries cannot be served.
DASHBOARD_CACHE_KEY = "dashboard:overview:v1"
DEFAULT_CACHE_TTL = 300
# Each one is a sequential LLM round-trip inside the request, on top of the
# explain + recommendation calls. 20 could not finish inside the gunicorn
# --timeout 120 on a real corpus; the worker was killed before the result
# was cached, so the next request repeated the whole thing.
DEFAULT_SENTIMENT_LIMIT = 8
DEFAULT_EXPLAIN_MAX_CHARS = 4000
AI_UNAVAILABLE_MESSAGE = "AI insights are temporarily unavailable"


def _int_setting(name, default):
    """Read an integer knob from settings, falling back to the environment."""
    value = getattr(settings, name, None)
    if value is None:
        value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        logger.warning("Invalid value for %s, using default %s", name, default)
        return default


def _server_error(detail=None):
    message = "Internal Server Error"
    if detail is not None and getattr(settings, "DEBUG", False):
        message = f"{message} : {detail}"
    return Response({
        "status": 500,
        "message": message,
        "response": None
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _cache_get(key):
    try:
        return cache.get(key)
    except Exception:
        logger.warning("Dashboard cache read failed for %s", key, exc_info=True)
        return None


def _cache_set(key, value, timeout):
    try:
        cache.set(key, value, timeout)
    except Exception:
        logger.warning("Dashboard cache write failed for %s", key, exc_info=True)


def _cache_delete(key):
    try:
        cache.delete(key)
    except Exception:
        logger.warning("Dashboard cache delete failed for %s", key, exc_info=True)


def _dominant_sentiment(values):
    if not values:
        return "neutral"
    try:
        return statistics.mode(values)
    except statistics.StatisticsError:
        # Empty input or (on older Pythons) a tie between sentiments.
        return Counter(values).most_common(1)[0][0]


# Create your views here.
class HandleDashboard(APIView):
    def get(self, request):
        try:
            dashboards = Dashboard.objects.all()
            serializer = DashboardSerializer(dashboards, many=True)
            return Response({
                "status": 200,
                "message": "Success",
                "response": {
                    "dashboards": serializer.data
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to list dashboards")
            return _server_error(e)


class GetDashboard(APIView):
    throttle_scope = "dashboard"
    def get_permissions(self):
        # Deleting an article is destructive, so it always needs a real user.
        if self.request.method == "DELETE":
            return [IsAuthenticated()]
        return super().get_permissions()

    def _sentiment_gemini(self, title, memo):
        key = (title or "").strip().lower()
        if key in memo:
            return memo[key]
        response = generate_text(
            f"between positive and negative sentiment, what is the sentiment of {title}"
        )
        memo[key] = response
        return response

    def _classify(self, response):
        lowered = (response or "").lower()
        if "positive" in lowered:
            return "positive"
        if "negative" in lowered:
            return "negative"
        return "neutral"

    def _build_dashboard(self):
        sentiment_limit = _int_setting("DASHBOARD_SENTIMENT_LIMIT", DEFAULT_SENTIMENT_LIMIT)
        explain_max_chars = _int_setting("DASHBOARD_EXPLAIN_MAX_CHARS", DEFAULT_EXPLAIN_MAX_CHARS)

        data = {}
        data_article = []
        data_article_explain = []
        data_article_views = []
        data_article_sentiment = []
        sentiment_memo = {}
        ai_available = True
        analysed = 0

        articles = list(Articles.objects.all().order_by("id"))
        article_ids = [article.id for article in articles]

        # Pull the related rows in three queries instead of three per article.
        first_sections = {}
        for section in Section.objects.filter(article_id__in=article_ids).order_by("id"):
            first_sections.setdefault(section.article_id, section)

        first_stamps = {}
        for stamp in ArticleStamp.objects.filter(article_id__in=article_ids).order_by("id"):
            first_stamps.setdefault(stamp.article_id, stamp)

        stored_sentiments = {}
        for stored in ArticleSentiment.objects.filter(article_id__in=article_ids).order_by("id"):
            stored_sentiments.setdefault(stored.article_id, stored)

        for article in articles:
            section = first_sections.get(article.id)
            if section is None:
                continue
            article_stamp = first_stamps.get(article.id)
            if article_stamp is None:
                continue

            article_data = {}
            article_data["title"] = article.title
            article_data["id"] = article.id
            article_data["description"] = section.body
            data_article_explain.append(section.body)
            article_data["count_view"] = article_stamp.count_view
            data_article_views.append(article_stamp.count_view)

            article_sentiment = stored_sentiments.get(article.id)
            if article_sentiment is None:
                article_sentiment = ArticleSentiment.objects.create(
                    article=article, sentiment="neutral", score=0.0
                )
                stored_sentiments[article.id] = article_sentiment

            sentiment = article_sentiment.sentiment or "neutral"
            if ai_available and analysed < sentiment_limit:
                try:
                    response = self._sentiment_gemini(article.title, sentiment_memo)
                except LLMUnavailable:
                    logger.warning("Model backend unavailable, keeping stored sentiments", exc_info=True)
                    ai_available = False
                else:
                    analysed += 1
                    sentiment = self._classify(response)
                    if article_sentiment.sentiment != sentiment:
                        article_sentiment.sentiment = sentiment
                        article_sentiment.save(update_fields=["sentiment"])

            article_data["sentiment"] = sentiment
            data_article_sentiment.append(sentiment)
            data_article.append(article_data)

        explain = ""
        recommendation = ""
        # Bound the prompt by characters: the article bodies are unbounded text.
        ai_explain = " ".join(data_article_explain)[:explain_max_chars]
        if data_article_views:
            average_views = sum(data_article_views) // len(data_article_views)
        else:
            average_views = 0

        if ai_available and ai_explain:
            try:
                explain = generate_text(f"explain {ai_explain}")
            except LLMUnavailable:
                logger.warning("Model backend unavailable while explaining articles", exc_info=True)
                ai_available = False

        if ai_available and data_article:
            try:
                recommendation = generate_text(
                    f"recommend me an article based on {average_views} views"
                )
            except LLMUnavailable:
                logger.warning("Model backend unavailable while recommending articles", exc_info=True)
                ai_available = False

        if not ai_available:
            explain = explain or AI_UNAVAILABLE_MESSAGE
            recommendation = recommendation or AI_UNAVAILABLE_MESSAGE

        data["articles"] = data_article
        data["explain"] = explain
        data["recommendation"] = recommendation
        data["views"] = sum(data_article_views)
        data["sentiment"] = _dominant_sentiment(data_article_sentiment)
        data["count"] = len(data_article)
        data["ai_available"] = ai_available
        return data

    def get(self, request):
        try:
            timeout = _int_setting("DASHBOARD_CACHE_TTL", DEFAULT_CACHE_TTL)
            refresh = str(request.query_params.get("refresh", "")).lower() in ("1", "true", "yes")

            data = None if refresh else _cache_get(DASHBOARD_CACHE_KEY)
            if data is None:
                data = self._build_dashboard()
                if timeout > 0:
                    _cache_set(DASHBOARD_CACHE_KEY, data, timeout)

            return Response({
                "status": 200,
                "message": "Success",
                "response": data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to build the dashboard")
            return _server_error(e)

    def delete(self, request):
        try:
            article_id = request.data.get("article_id")
            if article_id in (None, ""):
                return Response({
                    "status": 400,
                    "message": "Bad Request",
                    "response": {"article_id": "This field is required."}
                }, status=status.HTTP_400_BAD_REQUEST)
            try:
                article = Articles.objects.get(id=article_id)
            except (Articles.DoesNotExist, ValueError, TypeError):
                return Response({
                    "status": 404,
                    "message": "Not Found",
                    "response": None
                }, status=status.HTTP_404_NOT_FOUND)
            article.delete()
            _cache_delete(DASHBOARD_CACHE_KEY)
            return Response({
                "status": 200,
                "message": "Success",
                "response": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Failed to delete article from the dashboard")
            return _server_error(e)
