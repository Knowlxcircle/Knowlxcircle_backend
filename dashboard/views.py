from django.shortcuts import render
from .models import Dashboard
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from gemini.models import GeminiResponse, Prompt
from article.models import Articles, ArticleSentiment, Comment, ArticleStamp, Section
from gemini.views import model
import statistics

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
            data = {}
            data_article = []
            data_article_explain = []
            data_article_views = []
            data_article_sentiment = []

            articles = Articles.objects.all()
            
            for article in articles:
                article_data = {}
                section = Section.objects.filter(article=article)
                if len(section) == 0:
                    continue
                article_stamp = ArticleStamp.objects.filter(article=article).first()
                article_data["title"] = article.title
                article_data["id"] = article.id
                article_data["description"] = section[0].body
                data_article_explain.append(section[0].body)
                article_data["count_view"] = article_stamp.count_view
                data_article_views.append(article_stamp.count_view)
                article_sentiment = ArticleSentiment.objects.get_or_create(article=article)
                response = model.generate_content(f"between positive and negative sentiment, what is the sentiment of {article.title}")
                response = response.choices[0].text
                if "positive" in response.lower():
                    article_data["sentiment"] = "positive"
                elif "negative" in response.lower():
                    article_data["sentiment"] = "negative"
                else:
                    article_data["sentiment"] = "neutral"
                article_sentiment.sentiment = article_data["sentiment"]
                data_article_sentiment.append(article_data["sentiment"])
                data_article.append(article_data)
                
            data["articles"] = data_article
            ai_explain = "".join(data_article_explain[:100])
            response = model.generate_content(f"explain {ai_explain}")
            data["explain"] = response.choices[0].text
            ai_recommendation = sum(data_article_views) // len(data_article_views)
            response = model.generate_content(f"recommend me an article based on {ai_recommendation} views")
            data["recommendation"] = response.choices[0].text
            data["views"] = sum(data_article_views)
            data["sentiment"] = statistics.mode(data_article_sentiment)
            data["count"] = len(data_article)
            
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
            
    def delete(self, request):
        try:
            article_id = request.data.get("article_id")
            article = Articles.objects.get(id=article_id)
            article.delete()
            return Response({
                "status": 200,
                "message": "Success"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "status": 500,
                "message": f"Internal Server Error : {e}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)