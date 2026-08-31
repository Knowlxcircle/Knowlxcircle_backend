import ast
import json
import logging
import operator
import re
from functools import reduce

from django.conf import settings
from django.db import transaction
from django.db.models import Count, F, Prefetch, Q
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from gemini.client import LLMUnavailable, generate_text
from gemini.models import Prompt, GeminiResponse

from .models import Articles, Section, Comment, ArticleStamp
from .serializers import ArticleSerializer, SectionSerializer, CommentSerializer

logger = logging.getLogger(__name__)

# A generated keyword list longer than this is model noise, not a search.
MAX_KEYWORDS = 20

# "1. ", "2) ", "- ", "* ", "• " at the start of a line.
LIST_MARKER_RE = re.compile(r"^\s*(?:\d+\s*[\.\)]|[-*•])\s+")


def envelope(http_status, message, payload=None, **extra):
    """Every response in this project uses the same three-key envelope."""
    body = {
        "status": http_status,
        "message": message,
        "response": payload,
    }
    body.update(extra)
    return Response(body, status=http_status)


def server_error(exc, context, payload=None):
    """Log the real error, leak it to the client only while DEBUG is on."""
    logger.exception("%s failed: %s", context, exc)
    message = f"Internal Server Error : {exc}" if settings.DEBUG else "Internal Server Error"
    return envelope(status.HTTP_500_INTERNAL_SERVER_ERROR, message, payload)


def request_data(request):
    """request.data is a QueryDict/dict for the payloads we accept; an
    unparseable, array or scalar body must not turn every .get() into a 500 -
    it falls through to the serializer, which answers 400."""
    try:
        data = request.data
    except ParseError as e:
        logger.warning("Unparseable request body: %s", e)
        return {}
    return data if hasattr(data, "get") else {}


def extract_bracketed(text):
    """Return the first balanced [...] block in text, or None."""
    start = text.find("[")
    if start == -1:
        return None
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def stringify_items(parsed):
    """Flatten a parsed literal into a list of non-empty strings."""
    if not isinstance(parsed, (list, tuple)):
        return []
    items = []
    for entry in parsed:
        if isinstance(entry, str):
            entry = entry.strip()
        elif isinstance(entry, (list, tuple, dict)):
            entry = json.dumps(entry, ensure_ascii=False)
        else:
            entry = str(entry)
        if entry:
            items.append(entry)
    return items


def parse_list_block(text):
    """json.loads first, then ast.literal_eval, on the first [...] block."""
    if not text:
        return [], None
    block = extract_bracketed(text)
    if block is None:
        return [], None
    for loader in (json.loads, ast.literal_eval):
        try:
            items = stringify_items(loader(block))
        except Exception:
            items = []
        if items:
            return items, block
    return [], block


def parse_keywords(text):
    """Best-effort keyword list out of whatever the model produced."""
    items, block = parse_list_block(text)
    if items:
        return items
    inner = block[1:-1] if block else (text or "")
    keywords = []
    for part in re.split(r"[,\n]", inner):
        part = part.strip().strip("[]").strip().strip("\"'").strip()
        # A "keyword" longer than a title is prose, not a keyword.
        if part and len(part) <= 100:
            keywords.append(part)
    return keywords


def parse_sections(text):
    """Turn generated text into a list of section bodies.

    Tries a real Python/JSON list first, then numbered or bulleted lines,
    then blank-line separated paragraphs. Returns [] when nothing is usable.
    """
    items, _block = parse_list_block(text)
    if items:
        return items
    if not text:
        return []
    lines = text.splitlines()
    marked = [line for line in lines if LIST_MARKER_RE.match(line)]
    if marked:
        # Only the marked lines: a "Here are the steps:" preamble is not a section.
        bullets = [LIST_MARKER_RE.sub("", line).strip() for line in marked]
        bullets = [bullet for bullet in bullets if bullet]
        if bullets:
            return bullets
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text)]
    return [paragraph for paragraph in paragraphs if paragraph]


def dedupe(values):
    seen = set()
    unique = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            unique.append(value)
    return unique


# Create your views here.
class HandleArticle(APIView):
    def get(self, request):
        try:
            articles = Articles.objects.all()
            serializer = ArticleSerializer(articles, many=True)
            return envelope(status.HTTP_200_OK, "Success", serializer.data)
        except Exception as e:
            return server_error(e, "HandleArticle.get", [])

    def post(self, request):
        try:
            data = request_data(request)
            payload = {
                "title": data.get("title"),
                "author": data.get("author"),
            }
            published = data.get("published")
            if published is not None:
                payload["published"] = published

            serializer = ArticleSerializer(data=payload)
            if not serializer.is_valid():
                return envelope(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid article payload",
                    {},
                    errors=serializer.errors,
                )
            article = serializer.save()

            response_data = {}
            response_data["id"] = article.id
            response_data["title"] = article.title
            response_data["author"] = article.author

            return envelope(status.HTTP_201_CREATED, "Created", response_data)
        except Exception as e:
            return server_error(e, "HandleArticle.post", {})

    def put(self, request):
        try:
            data = request_data(request)
            article_id = data.get("id")
            try:
                article = Articles.objects.get(id=article_id)
            except (Articles.DoesNotExist, ValueError, TypeError):
                return envelope(status.HTTP_404_NOT_FOUND, "Article not found", {})

            payload = {}
            for field in ("title", "author", "published"):
                value = data.get(field)
                if value is not None:
                    payload[field] = value

            serializer = ArticleSerializer(article, data=payload, partial=True)
            if not serializer.is_valid():
                return envelope(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid article payload",
                    {},
                    errors=serializer.errors,
                )
            article = serializer.save()
            # One stamp per article: creating a new row on every update piled
            # up duplicates that the dashboard then read at random.
            ArticleStamp.objects.get_or_create(article=article)

            response_data = {}
            response_data["title"] = article.title
            response_data["author"] = article.author
            response_data["updated_at"] = article.updated_at
            return envelope(status.HTTP_200_OK, "Success", response_data)
        except Exception as e:
            return server_error(e, "HandleArticle.put", {})

class HandleSection(APIView):
    def get(self, request):
        try:
            sections = Section.objects.all()
            serializer = SectionSerializer(sections, many=True)
            return envelope(status.HTTP_200_OK, "Success", serializer.data)
        except Exception as e:
            return server_error(e, "HandleSection.get", [])

    def post(self, request):
        try:
            data = request_data(request)
            article_id = data.get("article_id")
            try:
                article = Articles.objects.get(id=article_id)
            except (Articles.DoesNotExist, ValueError, TypeError):
                return envelope(status.HTTP_404_NOT_FOUND, "Article not found", {})

            serializer = SectionSerializer(data={
                "article": article.pk,
                "body": data.get("body"),
                "order": data.get("order"),
            })
            if not serializer.is_valid():
                return envelope(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid section payload",
                    {},
                    errors=serializer.errors,
                )
            section = serializer.save()

            response_data = {}
            response_data["article"] = article.title
            response_data["body"] = section.body
            response_data["order"] = section.order

            return envelope(status.HTTP_200_OK, "Success", response_data)
        except Exception as e:
            return server_error(e, "HandleSection.post", {})

    # when user wants to change the order of the sections or update the body of the section
    def put(self, request):
        try:
            data = request_data(request)
            section_id = data.get("id")
            try:
                section = Section.objects.get(id=section_id)
            except (Section.DoesNotExist, ValueError, TypeError):
                return envelope(status.HTTP_404_NOT_FOUND, "Section not found", {})

            payload = {}
            for field in ("body", "order"):
                value = data.get(field)
                if value is not None:
                    payload[field] = value

            serializer = SectionSerializer(section, data=payload, partial=True)
            if not serializer.is_valid():
                return envelope(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid section payload",
                    {},
                    errors=serializer.errors,
                )
            section = serializer.save()

            response_data = {}
            response_data["article"] = section.article.title
            response_data["body"] = section.body
            response_data["order"] = section.order
            response_data["updated_at"] = section.updated_at
            return envelope(status.HTTP_200_OK, "Success", response_data)
        except Exception as e:
            return server_error(e, "HandleSection.put", {})

class HandleComment(APIView):
    def get(self, request):
        try:
            comments = Comment.objects.all()
            serializer = CommentSerializer(comments, many=True)
            return envelope(status.HTTP_200_OK, "Success", serializer.data)
        except Exception as e:
            return server_error(e, "HandleComment.get", [])

    def post(self, request):
        try:
            data = request_data(request)
            article_id = data.get("article_id")
            try:
                article = Articles.objects.get(id=article_id)
            except (Articles.DoesNotExist, ValueError, TypeError):
                return envelope(status.HTTP_404_NOT_FOUND, "Article not found", {})

            serializer = CommentSerializer(data={
                "article": article.pk,
                "body": data.get("body"),
                "author": data.get("author"),
            })
            if not serializer.is_valid():
                return envelope(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid comment payload",
                    {},
                    errors=serializer.errors,
                )
            comment = serializer.save()

            response_data = {}
            response_data["article"] = article.title
            response_data["body"] = comment.body
            response_data["author"] = comment.author

            return envelope(status.HTTP_200_OK, "Success", response_data)
        except Exception as e:
            return server_error(e, "HandleComment.post", {})

    def put(self, request):
        try:
            data = request_data(request)
            comment_id = data.get("id")
            try:
                comment = Comment.objects.get(id=comment_id)
            except (Comment.DoesNotExist, ValueError, TypeError):
                return envelope(status.HTTP_404_NOT_FOUND, "Comment not found", {})

            payload = {}
            for field in ("body", "author"):
                value = data.get(field)
                if value is not None:
                    payload[field] = value

            serializer = CommentSerializer(comment, data=payload, partial=True)
            if not serializer.is_valid():
                return envelope(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid comment payload",
                    {},
                    errors=serializer.errors,
                )
            comment = serializer.save()

            response_data = {}
            response_data["article"] = comment.article.title
            response_data["body"] = comment.body
            response_data["author"] = comment.author
            response_data["updated_at"] = comment.updated_at
            return envelope(status.HTTP_200_OK, "Success", response_data)
        except Exception as e:
            return server_error(e, "HandleComment.put", {})


class SearchArticle(APIView):
    def get(self, request):
        return self.search(request)

    def post(self, request):
        return self.search(request)

    def search(self, request):
        try:
            # A GET has no body, so the query has to come off the query string.
            search_query = (
                request.query_params.get("q")
                or request.query_params.get("query")
                or ""
            )
            if not search_query:
                data = request_data(request)
                search_query = data.get("q") or data.get("query") or ""
            search_query = str(search_query).strip()
            if not search_query:
                return envelope(
                    status.HTTP_400_BAD_REQUEST,
                    "A non-empty 'q' (or 'query') parameter is required",
                    [],
                )

            keywords = [search_query]
            try:
                generated = generate_text(
                    "Return ONLY a JSON array of 5-10 short search keywords for the topic "
                    + search_query
                    + '. Respond with the raw JSON array and nothing else, e.g. ["alpha","beta"].'
                )
                keywords.extend(parse_keywords(generated))
            except LLMUnavailable as e:
                # No API key / SDK trouble: still a usable search on the raw query.
                logger.warning("Keyword expansion unavailable, using the raw query: %s", e)
            except Exception as e:
                logger.exception("Keyword expansion failed, using the raw query: %s", e)

            # search_query is always present, so the reduce below is never empty.
            keywords = dedupe(keywords)[:MAX_KEYWORDS]
            title_filter = reduce(
                operator.or_,
                (Q(title__icontains=keyword) for keyword in keywords),
            )
            articles = Articles.objects.filter(title_filter).distinct().order_by("-created_at")

            list_article = [{"id": article.id, "title": article.title} for article in articles]

            return envelope(status.HTTP_200_OK, "Success", list_article)
        except Exception as e:
            return server_error(e, "SearchArticle", [])

class HandleGeminiArticle(APIView):
    def delete(self, request, id=None):
        try:
            if id is None:
                return envelope(status.HTTP_400_BAD_REQUEST, "An article id is required", {})
            try:
                article = Articles.objects.get(id=id)
            except Articles.DoesNotExist:
                return envelope(status.HTTP_404_NOT_FOUND, "Article not found", {})
            article.delete()
            return envelope(status.HTTP_200_OK, "Success", "Article deleted successfully")
        except Exception as e:
            return server_error(e, "HandleGeminiArticle.delete", {})

    def post(self, request, id=None):
        try:
            data = request_data(request)
            article_query = str(data.get("query") or "").strip()
            if not article_query:
                return envelope(
                    status.HTTP_400_BAD_REQUEST,
                    "A non-empty 'query' field is required",
                    {},
                )

            # 1. Generate. A missing key or an SDK failure is not a server bug.
            try:
                generated_text = generate_text(
                    f"Write a short article about {article_query} as a JSON array of strings, "
                    "one array element per paragraph. Respond with the raw JSON "
                    'array and nothing else, e.g. ["first para","second para"].'
                )
            except LLMUnavailable as e:
                logger.warning("The model backend is unavailable for article generation: %s", e)
                return envelope(
                    status.HTTP_503_SERVICE_UNAVAILABLE,
                    "The article generator is unavailable right now",
                    {},
                    data="Cannot generate content for the article",
                )
            except Exception as e:
                return server_error(e, "HandleGeminiArticle.post (generate)", {})

            # 2. Parse. Never exec() model output - literal_eval already has it.
            sections = parse_sections(generated_text)
            if not sections:
                logger.warning(
                    "Gemini returned nothing usable for %r: %r", article_query, generated_text[:200]
                )
                return envelope(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "Cannot generate content for the article",
                    {},
                    data="Cannot generate content for the article",
                )

            # 3. Persist. All or nothing: a half-written article (no sections)
            #    is exactly the state the dashboard chokes on. Nothing returns
            #    from inside the block, because a return would commit it.
            try:
                with transaction.atomic():
                    prompt = Prompt.objects.create(prompt=article_query[:300])
                    GeminiResponse.objects.create(prompt=prompt, response=generated_text)
                    article = Articles.objects.create(
                        title=article_query[:100], author="Gemini AI", published=False
                    )
                    created_sections = [
                        Section.objects.create(article=article, body=body, order=index)
                        for index, body in enumerate(sections)
                    ]
            except Exception as e:
                return server_error(e, "HandleGeminiArticle.post (persist)", {})

            article_data = ArticleSerializer(article).data
            article_data["sections"] = SectionSerializer(created_sections, many=True).data

            return envelope(status.HTTP_201_CREATED, "Created", article_data)
        except Exception as e:
            return server_error(e, "HandleGeminiArticle.post", {})

class HandleFullArticle(APIView):
    def get(self, request, id):
        try:
            try:
                article = Articles.objects.get(id=id)
            except Articles.DoesNotExist:
                return envelope(status.HTTP_404_NOT_FOUND, "Article not found", {})

            article_data = ArticleSerializer(article).data
            sections = Section.objects.filter(article=article).order_by("order")
            comments = Comment.objects.filter(article=article).order_by("created_at")
            article_data["sections"] = SectionSerializer(sections, many=True).data
            article_data["comments"] = CommentSerializer(comments, many=True).data

            # Atomic increment: read-modify-write lost views under concurrency.
            article_stamp, _created = ArticleStamp.objects.get_or_create(article=article)
            ArticleStamp.objects.filter(pk=article_stamp.pk).update(
                count_view=F("count_view") + 1
            )

            return envelope(status.HTTP_200_OK, "Success", article_data)
        except Exception as e:
            return server_error(e, "HandleFullArticle.get", {})

class GetArticles(APIView):
    def get(self, request):
        try:
            # Articles with no sections are deliberately hidden - the frontend
            # relies on it - so the filter lives in the queryset now.
            articles = (
                Articles.objects.annotate(section_total=Count("section"))
                .filter(section_total__gt=0)
                .order_by("-created_at")
                .prefetch_related(
                    Prefetch(
                        "section_set",
                        queryset=Section.objects.order_by("order"),
                        to_attr="ordered_sections",
                    ),
                    Prefetch(
                        "comment_set",
                        queryset=Comment.objects.order_by("created_at"),
                        to_attr="ordered_comments",
                    ),
                )
            )

            article_data = []
            for article in articles:
                article_dict = ArticleSerializer(article).data
                article_dict["sections"] = SectionSerializer(
                    article.ordered_sections, many=True
                ).data
                article_dict["comments"] = CommentSerializer(
                    article.ordered_comments, many=True
                ).data
                article_data.append(article_dict)

            return envelope(status.HTTP_200_OK, "Success", article_data)
        except Exception as e:
            return server_error(e, "GetArticles.get", [])
