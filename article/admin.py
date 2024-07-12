from django.contrib import admin
from .models import Articles, Section, Comment
# Register your models here.

admin.site.register(Articles)
admin.site.register(Section)
admin.site.register(Comment)
