import json

import openai
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from openai import OpenAI
from pydantic import BaseModel
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai.models import GPTChain, Message
from programs.models import Program, Wizard, StepType, Step, Product, WizardType, Nsi
from programs.serializers import StepSerializer, ProductSerializer

# Установите ключ OpenAI
openai.api_key = settings.OPENAI_API_KEY



class NsiModel(BaseModel):
    name: str
    year: str
    author: str
class ProductModel(BaseModel):
    name: str
    nsis: list[NsiModel]

class Res1(BaseModel):
    products: list[ProductModel]


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

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=messages,
        response_format=Res1
    )
    result_json = json.loads(completion.choices[0].message.content)

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

class IshDataProductsWizardView(APIView):
    def get(self, request, program_id):
        # Получаем объект Program или возвращаем 404
        program = get_object_or_404(Program, id=program_id)
        wizard_type = get_object_or_404(WizardType, code='ish_data_products')
        wizard, created = Wizard.objects.get_or_create(
            program=program,
            wizard_type=wizard_type,
            defaults={
                'created_at': timezone.now()  # Указать, если нужно установить текущую дату и время
            }
        )

        chain, chain_created = GPTChain.objects.get_or_create(
            wizard=wizard,
            defaults={
                'created_at': timezone.now()
            }
        )

        # Получаем все StepType для текущего WizardType
        step_types = StepType.objects.filter(wizard_type=wizard_type)

        # Находим первый StepType с position=1
        first_step_type = step_types.filter(position=1).first()

        # Количество StepType
        step_type_count = step_types.count()

        step_created = False
        if created and first_step_type:
            Step.objects.create(
                wizard=wizard,
                step_type=first_step_type,
                created_at=timezone.now(),
            )
            step_created = True
        # Проверяем, был ли объект создан, или он уже существовал
        if created:
            message = "Создан новый Wizard"
        else:
            message = "Найден существующий Wizard"

        steps = wizard.steps.all().values(
            'id', 'step_type__name', 'step_type__code', 'created_at', 'chunks', 'result'
        )

        # Подготавливаем ответ
        message = {
            'wizard_id': wizard.id,
            'chain_id': chain.id,
            'wizard_program': str(wizard.program),
            'wizard_type': str(wizard.wizard_type),
            'step_type_count': step_type_count,
            'steps': StepSerializer(wizard.steps.all(), many=True).data,
        }

        # Возвращаем ответ
        return JsonResponse(message, json_dumps_params={'ensure_ascii': False})

class ish_data_products_step_1(APIView):
    def post(self, request, program_id):
        program = get_object_or_404(Program, id=program_id)
        wizard = get_object_or_404(Wizard, program=program, wizard_type__code='ish_data_products')
        wizard_type = wizard.wizard_type
        step_types = StepType.objects.filter(wizard_type=wizard_type)
        chain = get_object_or_404(GPTChain, wizard=wizard)

        step_position = 1
        step = get_object_or_404(Step, wizard=wizard, step_type__position=step_position)

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
        step = get_object_or_404(Step, wizard=wizard, step_type__position=step_position)

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
        print("KEK")
        program = get_object_or_404(Program, id=program_id)
        wizard = get_object_or_404(Wizard, program=program, wizard_type__code='ish_data_products')
        wizard_type = wizard.wizard_type
        step_types = StepType.objects.filter(wizard_type=wizard_type)
        chain = get_object_or_404(GPTChain, wizard=wizard)
        step_position = 3
        step = get_object_or_404(Step, wizard=wizard, step_type__position=step_position)
        # step.chunks = request.data
        # step.save()



        mes4 = get_file_content("ai/samples/1-1-1-4.txt")

        messages = [
            {"role": "user", "content": mes4},
        ]
        delete_messages(chain, step_position)
        res = send_message_to_chain_and_parse(chain, step, messages)
        print("KEK2")
        next_step_type = step_types.filter(position=step_position+1).first()
        delete_post_steps(wizard, next_step_type)
        get_or_create_step(wizard, next_step_type, res, True)

        return JsonResponse(
            {
                "steps": StepSerializer(wizard.steps.all(), many=True).data
            },
            json_dumps_params={'ensure_ascii': False}
        )

class ish_data_products_step_4(APIView):
    def post(self, request, program_id):
        program = get_object_or_404(Program, id=program_id)
        wizard = get_object_or_404(Wizard, program=program, wizard_type__code='ish_data_products')
        wizard_type = wizard.wizard_type
        step_types = StepType.objects.filter(wizard_type=wizard_type)
        chain = get_object_or_404(GPTChain, wizard=wizard)
        step_position = 4
        step = get_object_or_404(Step, wizard=wizard, step_type__position=step_position)
        step.chunks = request.data
        step.save()

        products_data = request.data.get('products', [])

        if not isinstance(products_data, list):
            return Response({"error": "Invalid 'products' format. It must be a list."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Удаляем все существующие продукты этой программы
        program.products.all().delete()

        # Создаём новые продукты и связанные Nsi
        created_products = []
        for index, product_data in enumerate(products_data):
            nsis_data = product_data.pop('nsis', [])
            product = Product.objects.create(
                program=program,
                position=index+1,
                name=product_data['name'],
            )
            for nsi_data in nsis_data:
                nsi, _ = Nsi.objects.get_or_create(
                    nsiFullName=f"{nsi_data['name']}, {nsi_data['year']}, {nsi_data['author']}",
                    program=program,
                    type_id=58
                )
                product.nsis.add(nsi)
            created_products.append(product)

        # Сериализуем созданные продукты
        serialized_products = ProductSerializer(created_products, many=True)

        # Возвращаем ответ
        return Response(serialized_products.data, status=status.HTTP_201_CREATED)


class IshDataNsisWizardView(APIView):
    def get(self, request, program_id):
        # Получаем объект Program или возвращаем 404
        program = get_object_or_404(Program, id=program_id)
        wizard_type = get_object_or_404(WizardType, code='ish_data_products')
        wizard, created = Wizard.objects.get_or_create(
            program=program,
            wizard_type=wizard_type,
            defaults={
                'created_at': timezone.now()  # Указать, если нужно установить текущую дату и время
            }
        )

        chain, chain_created = GPTChain.objects.get_or_create(
            wizard=wizard,
            defaults={
                'created_at': timezone.now()
            }
        )

        # Получаем все StepType для текущего WizardType
        step_types = StepType.objects.filter(wizard_type=wizard_type)

        # Находим первый StepType с position=1
        first_step_type = step_types.filter(position=1).first()

        # Количество StepType
        step_type_count = step_types.count()

        step_created = False
        if created and first_step_type:
            Step.objects.create(
                wizard=wizard,
                step_type=first_step_type,
                created_at=timezone.now(),
            )
            step_created = True
        # Проверяем, был ли объект создан, или он уже существовал
        if created:
            message = "Создан новый Wizard"
        else:
            message = "Найден существующий Wizard"

        steps = wizard.steps.all().values(
            'id', 'step_type__name', 'step_type__code', 'created_at', 'chunks', 'result'
        )

        # Подготавливаем ответ
        message = {
            'wizard_id': wizard.id,
            'chain_id': chain.id,
            'wizard_program': str(wizard.program),
            'wizard_type': str(wizard.wizard_type),
            'step_type_count': step_type_count,
            'steps': StepSerializer(wizard.steps.all(), many=True).data,
        }

        # Возвращаем ответ
        return JsonResponse(message, json_dumps_params={'ensure_ascii': False})