from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Articles, Section, Comment
from .serializers import ArticleSerializer, SectionSerializer, CommentSerializer
from gemini.models import Prompt, GeminiResponse
from gemini.views import model
import re

# Create your views here.
class HandleArticle(APIView):
    def get(self, request):
        try:
            articles = Articles.objects.all()
            serializer = ArticleSerializer(articles, many=True)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def post(self, request):
        try:
            article_title = request.data.get("title")
            article_author = request.data.get("author")
            article_published = request.data.get("published")
            article = Articles(title=article_title, author=article_author, published=article_published)
            article.save()

            response_data = {}
            response_data["title"] = article.title
            response_data["author"] = article.author

            return Response({
                "status": 200,
                "message": "Success",
                "response": response_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        try:
            article_id = request.data.get("id")
            article_title = request.data.get("title")
            article_author = request.data.get("author")
            article_published = request.data.get("published")
            article = Articles.objects.get(id=article_id)
            article.title = article_title
            article.author = article_author
            article.published = article_published
            article.save()

            response_data = {}
            response_data["title"] = article.title
            response_data["author"] = article.author
            response_data["updated_at"] = article.updated_at
            return Response({
                "status": 200,
                "message": "Success",
                "response": response_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class HandleSection(APIView):
    def get(self, request):
        try:
            sections = Section.objects.all()
            serializer = SectionSerializer(sections, many=True)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def post(self, request):
        try:
            article_id = request.data.get("article_id")
            section_body = request.data.get("body")
            section_order = request.data.get("order")
            article = Articles.objects.get(id=article_id)
            section = Section(article=article, body=section_body, order=section_order)
            section.save()

            response_data = {}
            response_data["article"] = article.title
            response_data["body"] = section.body
            response_data["order"] = section.order

            return Response({
                "status": 200,
                "message": "Success",
                "response": response_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # when user wants to change the order of the sections or update the body of the section
    def put(self, request):
        try:
            section_id = request.data.get("id")
            section_body = request.data.get("body")
            section_order = request.data.get("order")
            section = Section.objects.get(id=section_id)
            section.body = section_body
            section.order = section_order
            section.save()

            response_data = {}
            response_data["article"] = section.article.title
            response_data["body"] = section.body
            response_data["order"] = section.order
            response_data["updated_at"] = section.updated_at
            return Response({
                "status": 200,
                "message": "Success",
                "response": response_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class HandleComment(APIView):
    def get(self, request):
        try:
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def post(self, request):
        try:
            article_id = request.data.get("article_id")
            comment_body = request.data.get("body")
            comment_author = request.data.get("author")
            article = Articles.objects.get(id=article_id)
            comment = Comment(article=article, body=comment_body, author=comment_author)
            comment.save()

            response_data = {}
            response_data["article"] = article.title
            response_data["body"] = comment.body
            response_data["author"] = comment.author

            return Response({
                "status": 200,
                "message": "Success",
                "response": response_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        try:
            comment_id = request.data.get("id")
            comment_body = request.data.get("body")
            comment_author = request.data.get("author")
            comment = Comment.objects.get(id=comment_id)
            comment.body = comment_body
            comment.author = comment_author
            comment.save()

            response_data = {}
            response_data["article"] = comment.article.title
            response_data["body"] = comment.body
            response_data["author"] = comment.author
            response_data["updated_at"] = comment.updated_at
            return Response({
                "status": 200,
                "message": "Success",
                "response": response_data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchArticle(APIView):
    def get(self, request):
        try:
            data = {}
            search_list = []
            search_query = request.query_params.get("query")
            search_list.append(search_query)
            try:
                prompt = model.generate_content("build a keyword list for searching and filtering with " + search_query + " and convert it to list with this format [keyword1, keyword2, ...]")
                if(len(prompt.candidates) > 1):
                    prompt = prompt.candidates[0]

                start_index = prompt.text.find('[') + 1

                # Step 2: Extract the relevant substring
                keywords_str = prompt[start_index:]

                # Step 3: Remove all "
                keywords_str = keywords_str.replace('"', '')

                # Step 4: Split the string based on ','
                keywords_list = [keyword.strip() for keyword in keywords_str.split(',')]

                # Remove the last element if it's empty or contains ']'
                if keywords_list[-1].strip() in {']', ''}:
                    keywords_list = keywords_list[:-1]

                # Step 5: Remove whitespace from each element
                keywords_list = [keyword.replace(" ", "") for keyword in keywords_list]

                # Output the result
                print(keywords_list)

                prompt = Prompt.objects.create(prompt=search_query)
                prompt_response = GeminiResponse.objects.create(prompt=prompt, response=prompt_response.text)
                data["prompt"] = prompt.prompt
                data["response"] = prompt_response.text
                data["created_at"] = prompt_response.created_at
            except Exception as e:
                return Response(
                    {
                        "status": 500,
                        "message": f"Internal Server Error : {e}"
                     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            articles = Articles.objects.filter(title__icontains=search_query)

            serializer = ArticleSerializer(articles, many=True)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": serializer.data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class HandleGeminiArticle(APIView):
    def post(self, request):
        try:
            data = {}
            article_query = request.query_params.get("query")
            try:
                prompt = model.generate_content(f"{article_query}? make the output in list format in python")
                if(len(prompt.candidates) > 1):
                    prompt = prompt.candidates[0]
                list_pattern = re.compile(r'=\s*(\[[^\]]*\])', re.DOTALL)
                match = list_pattern.search(prompt.text)
                if match:
                    list_string = match.group(1)
                    
                    # Dictionary to store the evaluated code
                    namespace = {}
                    
                    # Execute the string as Python code
                    exec(f'cake_steps = {list_string}', namespace)
                    
                    # Extract the list from the namespace
                    cake_steps = namespace['cake_steps']
                else:
                    print("List not found in the string.")
                
                prompt = Prompt.objects.create(prompt=article_query)
                prompt_response = GeminiResponse.objects.create(prompt=prompt, response=prompt_response.text)
                article = Articles.objects.create(title=article_query, author="Gemini AI", published=False)
                article.save()
                
                article_data = ArticleSerializer(article)
                for step in cake_steps:
                    section = Section.objects.create(article=article, body=step, order=cake_steps.index(step))
                    section.save()
                    section_data = SectionSerializer(section)
                    article_data["sections"].append(section_data)
                return Response(
                    {
                        "status": 200,
                        "message": "Success",
                        "response": article_data
                    }, status=status.HTTP_200_OK
                )
                                
            except Exception as e:
                return Response({
                    "status": 200,
                    "message": "Success",
                    "data": "Cannot generate content for the article"
                })
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )