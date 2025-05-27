from django.db import models

from constructor_vo_server import settings
from programs.models import Program
from django.contrib.auth import get_user_model

User = get_user_model()

class LLMChain(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название цепочки")
    prompt = models.TextField(verbose_name="Промпт", blank=True, null=True)
    inputs = models.JSONField(
        verbose_name="Входные данные",
        default=dict,
        blank=True,
        null=True
    )
    file_url = models.CharField(max_length=500, verbose_name="Ссылка на файл")
    input_url = models.CharField(max_length=500, verbose_name="Ссылка на входные данные")
    use_results = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='used_by',
        verbose_name="Использует результаты цепочки"
    )
    result_template = models.CharField(max_length=500, blank=True, null=True, verbose_name="Шаблонизатор результата")

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор цепочки",
        blank=True, null=True
    )


    def __str__(self):
        return self.name


class LLMModel(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название модели")
    model_name = models.CharField(max_length=255, verbose_name="Название модели для кода", blank=True)
    api_url = models.URLField(max_length=500, verbose_name="API URL")
    api_key = models.CharField(max_length=255, verbose_name="API ключ")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.model_name:
            self.model_name = self.name
        super().save(*args, **kwargs)


class LLMChainRun(models.Model):
    chain = models.ForeignKey(LLMChain, on_delete=models.CASCADE, related_name="runs")
    model = models.ForeignKey(LLMModel, on_delete=models.SET_NULL, null=True, blank=True, related_name="runs")

    current_step = models.PositiveIntegerField(default=1)

    inputs = models.JSONField()       # входные данные (shared["inputs"])
    result = models.JSONField(null=True, blank=True)  # итоговый JSON (shared["final_result"] или подобное)

    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="llm_chain_runs",
        verbose_name="Программа ОП"
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("in_progress", "В процессе"),
            ("completed", "Завершено"),
            ("error", "Ошибка")
        ],
        default="in_progress"
    )

    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="llm_chain_runs",
        verbose_name="Пользователь"
    )

    def __str__(self):
        return f"Цепочка {self.chain_id} / Модель {self.model_id or '—'} / {self.status}"

class LLMMessage(models.Model):
    MESSAGE_TYPES = [
        ("system", "System"),
        ("user", "User"),
        ("assistant", "Assistant"),
        ("tool", "Tool"),
        ("raw", "Raw"),  # можно оставить для логов или нестандартных типов
    ]

    llm_chain_run = models.ForeignKey(
        LLMChainRun,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Запуск цепочки"
    )

    type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        verbose_name="Тип сообщения"
    )

    message = models.TextField(verbose_name="Текст сообщения")

    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")

    def __str__(self):
        return f"[{self.get_type_display()}] {self.message[:40]}..."