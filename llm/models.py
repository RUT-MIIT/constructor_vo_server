from django.db import models

class LLMChain(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название цепочки")
    file_url = models.CharField(max_length=500, verbose_name="Ссылка на файл")
    input_url = models.CharField(max_length=500, verbose_name="Ссылка на входные данные")

    def __str__(self):
        return self.name


class LLMModel(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название модели")
    api_url = models.URLField(max_length=500, verbose_name="API URL")
    api_key = models.CharField(max_length=255, verbose_name="API ключ")

    def __str__(self):
        return self.name
