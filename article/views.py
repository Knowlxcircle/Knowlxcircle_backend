from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Articles, Section, Comment, ArticleSentiment, ArticleStamp
from .serializers import ArticleSerializer, SectionSerializer, CommentSerializer
from gemini.models import Prompt, GeminiResponse
from gemini.views import model
import re
import ast

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
        # try:
            article_title = request.data.get("title")
            article_author = request.data.get("author")
            article_published = request.data.get("published")
            article = Articles(title=article_title, author=article_author, published=article_published)
            article.save()

            response_data = {}
            response_data["id"] = article.id
            response_data["title"] = article.title
            response_data["author"] = article.author

            return Response({
                "status": 200,
                "message": "Success",
                "response": response_data
            }, status=status.HTTP_200_OK)
        # except Exception as e:
        #     return Response(
        #         {
        #             "status": 500,
        #             "message": f"Internal Server Error : {e}"
        #          }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )

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
            article_stamp = ArticleStamp.objects.create(article=article)
            article_stamp.save()

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
        # try:
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
        # except Exception as e:
        #     return Response(
        #         {
        #             "status": 500,
        #             "message": f"Internal Server Error : {e}"
        #          }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        #     )
    
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
            search_query = request.data.get("query")
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
    def delete(self, request, id):
        try:
            article = Articles.objects.get(id=id)
            article.delete()
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": "Article deleted successfully"
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
            article_query = request.data.get("query")

            # Generate the content from the model
            try:
                query_prompt = f"{article_query}, convert your answer in list format like in python please"
                # print(query_prompt)
                generated_prompt = model.generate_content(query_prompt)

                # Select the first candidate if there are multiple
                if len(generated_prompt.candidates) > 1:
                    generated_text = generated_prompt.candidates[0].text
                else:
                    generated_text = generated_prompt.text
                # print(generated_text)

                # Regular expression to find the list in the generated text
                list_pattern = re.compile(r'=\s*(\[[\s\S]*?\])', re.DOTALL)
                match = list_pattern.search(generated_text)

                # Initialize cake_steps
                cake_steps = []
                # print("Match")
                # print(match)

                if match:
                    list_string = match.group(1)
                    try :
                        list_ast = ast.literal_eval(list_string)
                    except Exception as e:
                        return Response({
                        "status": 500,
                        "message": "Failed",
                        "data": "Cannot generate content for the article"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    # Dictionary to store the evaluated code
                    namespace = {}
                    
                    # Execute the string as Python code safely
                    try:
                        exec(f'cake_steps = {list_ast}', namespace)
                        cake_steps = namespace['cake_steps']
                        print(cake_steps)
                    except Exception as e:
                        print(f"Error executing the code: {e}")
                else:
                    print("List not found in the string.")
                    exec(f'cake_steps = {generated_text}', namespace)
                    cake_steps = namespace['cake_steps']

            # Create and save the prompt object
                prompt = Prompt.objects.create(prompt=article_query)
                prompt.save()
                # Create and save the prompt response object
                prompt_response = GeminiResponse.objects.create(prompt=prompt, response=generated_text)
                prompt_response.save()
                # Create and save the article object
                article = Articles.objects.create(title=article_query, author="Gemini AI", published=False)
                article.save()

                # Serialize the article data
                article_data = ArticleSerializer(article).data
                article_data["sections"] = []

                # Create and save sections based on cake_steps
                for index, step in enumerate(cake_steps):
                    section = Section.objects.create(article=article, body=step, order=index)
                    section.save()
                    section_data = SectionSerializer(section).data
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
                    "status": 500,
                    "message": "Failed",
                    "data": "Cannot generate content for the article"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class HandleFullArticle(APIView):
    def get(self, request, id):
        try:
            article = Articles.objects.get(id=id)
            article_data = ArticleSerializer(article).data
            sections = Section.objects.filter(article=article)
            comments = Comment.objects.filter(article=article)
            article_data["sections"] = []
            article_data["comments"] = []
            sorted_sections = sorted(sections, key=lambda x: x.order)
            for section in sorted_sections:
                section_data = SectionSerializer(section).data
                article_data["sections"].append(section_data)
            for comment in comments:
                comment_data = CommentSerializer(comment).data
                article_data["comments"].append(comment_data)
            article_stamp, created = ArticleStamp.objects.get_or_create(article=article)
            if not created:
                article_stamp.count_view += 1
            else:
                article_stamp.count_view = 1
            article_stamp.save()
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": article_data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
class GetArticles(APIView):
    def get(self, request):
        try:
            articles = Articles.objects.all()
            article_data = []
            for article in articles:
                article_dict = ArticleSerializer(article).data
                sections = Section.objects.filter(article=article)
                comments = Comment.objects.filter(article=article)
                article_dict["sections"] = []
                article_dict["comments"] = []
                sorted_sections = sorted(sections, key=lambda x: x.order)
                for section in sorted_sections:
                    section_data = SectionSerializer(section).data
                    article_dict["sections"].append(section_data)
                for comment in comments:
                    comment_data = CommentSerializer(comment).data
                    article_dict["comments"].append(comment_data)
                if len(article_dict["sections"]) != 0:
                    article_data.append(article_dict)
            return Response(
                {
                    "status": 200,
                    "message": "Success",
                    "response": article_data
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "status": 500,
                    "message": f"Internal Server Error : {e}"
                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )