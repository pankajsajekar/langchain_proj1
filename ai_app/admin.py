from django.contrib import admin

from .models import AIChats

class AIChatsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'message', 'response', 'tokens_used', 'created_at')
    search_fields = ('user__username', 'message', 'response')
    list_filter = ('created_at',)
admin.site.register(AIChats, AIChatsAdmin)