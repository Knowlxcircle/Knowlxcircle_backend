"""
URL configuration for knowlxcirclebackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
import markdown
from django.shortcuts import render

def markdown_view(request):
    with open('README.md', 'r') as file:
        content = file.read()
    html_content = markdown.markdown(content)
    return HttpResponse(html_content)


urlpatterns = [
    path("", markdown_view, name="home"),
    path("admin/", admin.site.urls),
    path("api/v1/gemini/", include("gemini.urls")),
    path("api/v1/dashboard/", include("dashboard.urls")),
    path("api/v1/auth/", include("authentication.urls")),
    path("api/v1/circle/", include("circle.urls")),
    path("api/v1/article/", include("article.urls")),
]
