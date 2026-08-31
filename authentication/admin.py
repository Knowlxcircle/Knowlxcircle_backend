from django.contrib import admin
from .models import Member, SocialMedia

# Register your models here.
@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'occupation')
    search_fields = ('user__username', 'occupation')

@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'platform', 'username')
    search_fields = ('platform', 'username')
