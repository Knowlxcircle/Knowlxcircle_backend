from django.contrib import admin
from .models import Circle, CircleMember, MemberSentiment

# Register your models here.
@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name", "description")

@admin.register(CircleMember)
class CircleMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "circle", "user", "role")
    list_filter = ("role",)

@admin.register(MemberSentiment)
class MemberSentimentAdmin(admin.ModelAdmin):
    list_display = ("id", "circle", "sentiment", "score", "created_at")
    list_filter = ("sentiment",)
