from django.shortcuts import render
from .models import Dashboard
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from gemini.models import GeminiResponse, Prompt
from article.models import Articles, ArticleSentiment, Comment, ArticleStamp, Section
from gemini.views import model
import statistics
import json
import os

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
    ai_explain_response = ""
    ai_recommendation = ""
    
    def article_sentiment_gemini(self, id, title):
        data = {}
        if id in data.keys():
            return data[id]
        else:
            response = model.generate_content(f"between positive and negative sentiment, what is the sentiment of {title}")
            response = response.text
            data[id] = response
            return response
            
    def article_explain_gemini(self, ai_explain):
        if self.ai_explain_response != "":
            return self.ai_explain_response
        response = model.generate_content(f"explain {ai_explain}")
        self.ai_explain_response = response.text
        return response.text

    def article_recommendation_gemini(self, ai_recommendation):
        if self.ai_recommendation != "":
            return self.ai_recommendation
        response = model.generate_content(f"recommend me an article based on {ai_recommendation} views")
        self.ai_recommendation = response.text
        return response.text
            
    def get(self, request):
        # try:
            json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.json")
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as json_file:
                    data = json.load(json_file)
            else:
                name = "Dashboard"
                if request.user.is_authenticated:
                    user = request.user
                else:
                    user = None
                description = "This is a dashboard"
                dashboard = Dashboard.objects.create(name=name, user=user, description=description)
                dashboard.save()
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
                    if article_stamp is None:
                        continue
                    article_data["title"] = article.title
                    article_data["id"] = article.id
                    article_data["description"] = section[0].body
                    data_article_explain.append(section[0].body)
                    article_data["count_view"] = article_stamp.count_view
                    data_article_views.append(article_stamp.count_view)
                    article_sentiment, created = ArticleSentiment.objects.get_or_create(article=article, sentiment="neutral", defaults={"score": 0.0})
                    article_sentiment_id = article_sentiment.id
                    response = self.article_sentiment_gemini(article_sentiment_id, article.title)
                    if "positive" in response.lower():
                        article_data["sentiment"] = "positive"
                    elif "negative" in response.lower():
                        article_data["sentiment"] = "negative"
                    else:
                        article_data["sentiment"] = "neutral"
                    article_sentiment.sentiment = article_data["sentiment"]
                    article_sentiment.save()  # Save the updated sentiment
                    data_article_sentiment.append(article_data["sentiment"])
                    data_article.append(article_data)
                    
                data["articles"] = data_article
                ai_explain = " ".join(data_article_explain[:100])  # Assuming you want a string with the first 100 words
                response = self.article_explain_gemini(ai_explain)
                data["explain"] = response
                ai_recommendation = sum(data_article_views) // len(data_article_views)
                response = self.article_recommendation_gemini(ai_recommendation)
                data["recommendation"] = response
                data["views"] = sum(data_article_views)
                data["sentiment"] = statistics.mode(data_article_sentiment)
                data["count"] = len(data_article)
                
                with open(json_file_path, 'w') as json_file:
                    json.dump(data, json_file)
                    
            return Response({
                "status": 200,
                "message": "Success",
                "response": data
            }, status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response({
        #         "status": 500,
        #         "message": f"Internal Server Error: {e}"
        #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
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
            
    
        
        