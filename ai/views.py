from django.shortcuts import render

import openai
from django.http import JsonResponse
from django.conf import settings
from openai import OpenAI
# Установите ключ OpenAI
openai.api_key = settings.OPENAI_API_KEY


def chat_with_gpt(request):

    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Write a haiku about recursion in programming."
            }
        ]
    )

    print(completion.choices[0].message)
