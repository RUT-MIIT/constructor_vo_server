from django.contrib import admin
from .models import LLMChain, LLMModel


@admin.register(LLMChain)
class LLMChainAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'file_url', 'input_url')
    search_fields = ('name',)
    list_display_links = ('id', 'name')


@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'api_url', 'api_key')
    search_fields = ('name',)
    list_display_links = ('id', 'name')
