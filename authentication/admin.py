from django.contrib import admin
from .models import Member, SocialMedia
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Member)
admin.site.register(SocialMedia)
admin.site.register(User)