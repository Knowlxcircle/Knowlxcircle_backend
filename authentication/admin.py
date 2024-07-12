from django.contrib import admin
from .models import User, SocialMedia

# Register your models here.
admin.site.register(User)
admin.site.register(SocialMedia)