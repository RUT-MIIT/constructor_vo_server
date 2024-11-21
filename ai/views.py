from django.shortcuts import render

import openai
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
# Установите ключ OpenAI
openai.api_key = settings.OPENAI_API_KEY


def chat_with_gpt(request):

    client = OpenAI(
        api_key= "sk-fBLtvCA7TpxepwcHzDjuVPIhhs1j1Iio",
        base_url="https://api.proxyapi.ru/openai/v1",
    )

    try:
        # Запрос к OpenAI Chat API
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Проанализируй контент файла https://storage.yandexcloud.net/cvotest1/fgos_files/OM.docx."
                }
            ]
        )

        # Возвращаем ответ как JSON
        return JsonResponse({
            "response": completion.choices[0].message.content
        })

    except Exception as e:
        # Обработка ошибок
        return JsonResponse({"error": str(e)}, status=500)
