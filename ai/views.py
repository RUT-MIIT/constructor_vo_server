from django.shortcuts import render

import openai
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from openai import OpenAI
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from ai.models import GPTChain, Message
from programs.models import Program, Wizard, StepType, Step
from django.utils import timezone

from programs.serializers import StepSerializer
from pydantic import BaseModel

import json
# Установите ключ OpenAI
openai.api_key = settings.OPENAI_API_KEY



class Nsi(BaseModel):
    name: str
    year: str
    author: str
class Product(BaseModel):
    name: str
    nsis: list[Nsi]

class Res1(BaseModel):
    products: list[Product]


def get_file_content(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()
    return file_content

def chat_with_gpt(request):

    client = OpenAI(
        api_key= settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
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


def delete_messages(chain, position):
    Message.objects.filter(
        step__step_type__position__gte=position,
        chain=chain
    ).delete()
    return True

def send_message_to_chain(chain, step, messages):
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    for message in messages:
        Message.objects.create(
            chain=chain,
            role=message["role"],
            content=message["content"],
            step=step
        )
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in chain.messages.all()
    ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    Message.objects.create(
        chain=chain,
        role="assistant",
        content=completion.choices[0].message.content,
        step=step
    )

    return completion.choices[0].message.content


def send_message_to_chain_and_parse(chain, step, messages):
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    for message in messages:
        Message.objects.create(
            chain=chain,
            role=message["role"],
            content=message["content"],
            step=step
        )
    messages = [
        {"role": msg.role, "content": msg.content}
        for msg in chain.messages.all()
    ]
    print("LOL")
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        response_format=Res1
    )
    result_json = json.loads(completion.choices[0].message.content)
    print("KEK")

    Message.objects.create(
        chain=chain,
        role="assistant",
        content=result_json,
        step=step
    )

    return result_json

def get_or_create_step(wizard,step_type,result,is_json):
    step, created = Step.objects.get_or_create(
        wizard=wizard,
        step_type=step_type,
        defaults={
            'created_at': timezone.now(),  # Устанавливаем дату создания, если Step создаётся
            'result': result if not is_json else None,
            'result_json': result if is_json else None
        }
    )
    return step

def delete_post_steps(wizard,step_type):
    Step.objects.filter(
        wizard=wizard,
        step_type__position__gte=step_type.position
    ).delete()
    return True
class ish_data_products_step_1(APIView):
    def post(self, request, program_id):
        program = get_object_or_404(Program, id=program_id)
        wizard = get_object_or_404(Wizard, program=program, wizard_type__code='ish_data_products')
        wizard_type = wizard.wizard_type
        step_types = StepType.objects.filter(wizard_type=wizard_type)
        chain = get_object_or_404(GPTChain, wizard=wizard)

        step_position = 1
        step = Step.objects.get(wizard=wizard, step_type__position=step_position)
        step.chunks = request.data
        step.save()

        methodologies = request.data['methodologies']
        methodologies_str = "\n".join([f"{item};" for item in methodologies])
        subject_scope = request.data['subject_scope']

        mes1 = get_file_content("ai/samples/1-1-1-1.txt")
        mes2 = get_file_content("ai/samples/1-1-1-2.txt")
        mes2 = mes2.replace('<!-- methodologies --!>', methodologies_str)
        mes3 = get_file_content("ai/samples/1-1-1-3.txt")
        mes3 = mes3.replace('<!-- subject_scope --!>', subject_scope)

        messages = [
            {"role": "system", "content": mes1},
            {"role": "system", "content": mes2},
            {"role": "user", "content": mes3},
        ]
        delete_messages(chain, step_position)
        res = send_message_to_chain(chain,step, messages)

        next_step_type = step_types.filter(position=step_position+1).first()
        delete_post_steps(wizard, next_step_type)
        get_or_create_step(wizard,next_step_type,res, False)

        return JsonResponse(
            {"steps": StepSerializer(wizard.steps.all(), many=True).data},
            json_dumps_params={'ensure_ascii': False}
        )


class ish_data_products_step_2(APIView):
    def post(self, request, program_id):
        program = get_object_or_404(Program, id=program_id)
        wizard = get_object_or_404(Wizard, program=program, wizard_type__code='ish_data_products')
        wizard_type = wizard.wizard_type
        step_types = StepType.objects.filter(wizard_type=wizard_type)
        chain = get_object_or_404(GPTChain, wizard=wizard)

        step_position = 2

        next_step_type = step_types.filter(position=step_position+1).first()
        delete_post_steps(wizard, next_step_type)
        get_or_create_step(wizard,next_step_type, None, False)

        return JsonResponse(
            {
                "steps": StepSerializer(wizard.steps.all(), many=True).data
            },
            json_dumps_params={'ensure_ascii': False}
        )


class ish_data_products_step_3(APIView):
    def post(self, request, program_id):
        program = get_object_or_404(Program, id=program_id)
        wizard = get_object_or_404(Wizard, program=program, wizard_type__code='ish_data_products')
        wizard_type = wizard.wizard_type
        step_types = StepType.objects.filter(wizard_type=wizard_type)
        chain = get_object_or_404(GPTChain, wizard=wizard)
        step_position = 3
        step = Step.objects.get(wizard=wizard, step_type__position=step_position)
        # step.chunks = request.data
        # step.save()



        mes4 = get_file_content("ai/samples/1-1-1-4.txt")

        messages = [
            {"role": "user", "content": mes4},
        ]
        delete_messages(chain, step_position)
        res = send_message_to_chain_and_parse(chain, step, messages)

        next_step_type = step_types.filter(position=step_position+1).first()
        delete_post_steps(wizard, next_step_type)
        get_or_create_step(wizard, next_step_type, res, True)

        return JsonResponse(
            {
                "steps": StepSerializer(wizard.steps.all(), many=True).data
            },
            json_dumps_params={'ensure_ascii': False}
        )