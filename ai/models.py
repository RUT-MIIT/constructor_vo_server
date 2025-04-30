from django.db import models
from django.contrib.auth import get_user_model
from programs.models import Program, Wizard, Step

User = get_user_model()


class GPTChain(models.Model):
    wizard = models.OneToOneField(Wizard, null=True, on_delete=models.CASCADE, related_name='chat')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Цепочка сообщение"
        verbose_name_plural = "Цепочки сообщений"

    def __str__(self):
        return f"Chat for {self.wizard}"


class Message(models.Model):
    ROLES = [
        ('user', 'user'),
        ('system', 'system'),
        ('assistant', 'assistant'),
    ]
    chain = models.ForeignKey(GPTChain, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default='Очная'
    )
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']  # Сортировка сообщений по времени
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


    def __str__(self):
        return f"Message from {self.role} in {self.chain}"

