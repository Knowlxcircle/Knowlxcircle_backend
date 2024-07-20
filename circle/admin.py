from django.contrib import admin
from .models import Circle, CircleMember, MemberSentiment

# Register your models here.
admin.site.register(Circle)
admin.site.register(CircleMember)
admin.site.register(MemberSentiment)
