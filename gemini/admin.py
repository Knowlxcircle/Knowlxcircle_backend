from django.contrib import admin
from .models import GeminiResponse, Prompt

# Register your models here.
admin.site.register(GeminiResponse)
admin.site.register(Prompt)
