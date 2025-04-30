from django.contrib import admin
from .models import GPTChain, Message

@admin.register(GPTChain)
class GPTChainAdmin(admin.ModelAdmin):
    list_display = ('wizard', 'created_at')  # Отображаемые поля в списке
    search_fields = ('wizard__id', 'wizard__program__profile')  # Поля для поиска
    list_filter = ('created_at',)  # Фильтр по дате создания
    ordering = ('-created_at',)  # Сортировка в обратном порядке по дате создания


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chain', 'role', 'step__step_type__name', 'created_at')  # Отображаемые поля в списке
    search_fields = ('chain__wizard__id', 'content')  # Поля для поиска
    list_filter = ('role', 'created_at')  # Фильтры для удобства
    ordering = ('-created_at',)  # Сортировка в обратном порядке по дате создания
