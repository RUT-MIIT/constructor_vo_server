from django.contrib import admin
from .models import LLMChain, LLMModel, LLMChainRun, LLMMessage


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


@admin.register(LLMChainRun)
class LLMChainRunAdmin(admin.ModelAdmin):
    list_display = (
        "id","user", "chain", "model", "current_step", "status", "created_at", "updated_at"
    )
    list_filter = ("status", "created_at", "model")
    search_fields = ("chain__name", "model__model_name")  # если у chain есть поле name
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)



@admin.register(LLMMessage)
class LLMMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "llm_chain_run", "type", "short_message", "timestamp")
    list_filter = ("type", "timestamp")
    search_fields = ("message", "llm_chain_run__id")
    readonly_fields = ("llm_chain_run", "type", "message", "timestamp")
    ordering = ("-timestamp",)

    def short_message(self, obj):
        return obj.message[:60] + ("..." if len(obj.message) > 60 else "")
    short_message.short_description = "Сообщение"