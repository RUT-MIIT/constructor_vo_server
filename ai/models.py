from django.db import models
from django.contrib.auth import get_user_model
from programs.models import Program, Stage

User = get_user_model()


class GPTChat(models.Model):
    stage = models.OneToOneField(Stage, on_delete=models.CASCADE, related_name='chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat for {self.stage}"


class Message(models.Model):
    ROLES = [
        ('user', 'user'),
        ('system', 'system'),
        ('assistant', 'assistant'),
    ]
    chat = models.ForeignKey(GPTChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages')
    role = models.CharField(
        max_length=20,
        choices=ROLES,
        default='Очная'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']  # Сортировка сообщений по времени

    def __str__(self):
        return f"Message from {self.sender} in {self.chat}"


class MessageFile(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='message_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_files'

    def __str__(self):
        return f"File for {self.message} ({self.file.name})"
