"""
URL configuration for knowlxcirclebackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

import markdown

# Rendering the README on every request is pure waste; it never changes while
# the process is alive.
_readme_html = None


def _render_readme():
    readme_path = settings.BASE_DIR / "README.md"
    try:
        source = readme_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # Missing or undecodable README (FileNotFoundError is an OSError):
        # serve a plain landing page instead of a traceback.
        return "<h1>Knowlxcircle API</h1><p>The API is running.</p>"
    return markdown.markdown(source)


def markdown_view(request):
    global _readme_html
    if _readme_html is None:
        _readme_html = _render_readme()
    return HttpResponse(_readme_html)


urlpatterns = [
    path("", markdown_view, name="home"),
    path("admin/", admin.site.urls),
    path("api/v1/gemini/", include("gemini.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/auth/", include("authentication.urls")),
    path("api/v1/circle/", include("circle.urls")),
    path("api/v1/article/", include("article.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
