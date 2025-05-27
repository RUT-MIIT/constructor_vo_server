import os
from urllib.parse import urljoin

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
import importlib
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
import json, os
from django.conf import settings
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



import ast

from constructor_vo_server import settings
from .forms import LoginForm, LLMChainForm

from llm.models import LLMChain, LLMModel, LLMChainRun
from programs.models import Program

from .pocketflow.main import run_flow

User = get_user_model()


def get_nested_attr(obj, attr_path):
    """Безопасный доступ к вложенным атрибутам: program.direction.code"""
    try:
        for attr in attr_path.split('.'):
            obj = getattr(obj, attr)
        return obj
    except Exception:
        return None

def fill_json_template(template_data, program, chain_run):
    inputs = {}

    chain_result = chain_run.result if chain_run is not None else None

    # 1. Первичный проход — обрабатываем db и input
    for field in template_data:
        source = field.get('source')
        value_path = field.get('value')

        if source == "db" and value_path.startswith("program."):
            attr_path = value_path[len("program."):]
            real_value = get_nested_attr(program, attr_path)
            field['value'] = real_value if real_value is not None else field.get('default', "")
            inputs[field['code']] = field['value']

        elif source == "input":
            if not field.get('value') and field.get('default'):
                field['value'] = field['default']
            inputs[field['code']] = field['value']

    function_inputs = {
        "chain_result": chain_result,
        "program": program,
    }

    # 2. Второй проход — обрабатываем function
    for field in template_data:

        if field.get('source') == "function":
            func_name = field.get('code')
            try:
                module = importlib.import_module("llm.functions")  # имя своего модуля
                func = getattr(module, func_name)
                result = func(function_inputs)
                field['value'] = result
                inputs[field['code']] = result
            except Exception as e:
                field['value'] = f"[Ошибка вызова функции: {e}]"
                inputs[field['code']] = None

    return template_data


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            form.add_error(None, 'Неверный email или пароль')

    return render(request, 'login.html', {'form': form})


def home_view(request):
    chains = LLMChain.objects.all()
    models = LLMModel.objects.all()
    programs = Program.objects.all()

    return render(request, 'home.html', {
        'chains': chains,
        'models': models,
        'programs': programs,
    })

def chains_view(request):
    chains = LLMChain.objects.all()

    return render(request, 'chains.html', {
        'chains': chains,

    })

def chain_detail(request, pk):
    chain = get_object_or_404(LLMChain, pk=pk)
    file_content = None
    error = None

    if chain.prompt:
        file_content = chain.prompt
    else:
        file_content = ""
    # 1. Чтение файла цепочки
    # if chain.file_url:
    #     file_path = os.path.join(settings.BASE_DIR, chain.file_url.lstrip('/'))
    #     file_path = os.path.normpath(file_path)
    #
    #     print("Файл цепочки:", file_path)
    #
    #     if not os.path.exists(file_path):
    #         error = "Файл цепочки не найден"
    #     else:
    #         try:
    #             with open(file_path, 'r', encoding='utf-8') as f:
    #                 file_content = f.read()
    #         except Exception as e:
    #             error = f"Ошибка чтения файла цепочки: {str(e)}"

    # 2. Чтение входного файла (если есть)
    template_data = None
    # if chain.input_url:
    #     input_path = os.path.join(settings.BASE_DIR, chain.input_url.lstrip('/'))
    #     input_path = os.path.normpath(input_path)
    #
    #     print("Входной файл:", input_path)
    #
    #     if not os.path.exists(input_path):
    #         raise Http404("Файл с входными данными не найден")
    #
    #     try:
    #         with open(input_path, 'r', encoding='utf-8') as f:
    #             template_data = json.load(f)
    #     except Exception as e:
    #         error = f"Ошибка чтения входного файла: {str(e)}"
    if chain.inputs:
        template_data = chain.inputs
    else:
        template_data = {}

    return render(request, 'chain_detail.html', {
        'chain': chain,
        'file_content': file_content,
        'template_data': template_data,
        'error': error
    })

def chain_edit(request, pk):
    chain = get_object_or_404(LLMChain, pk=pk)

    # Проверка прав — только автор может редактировать
    if request.user != chain.author:
        raise PermissionDenied("У вас нет прав редактировать эту цепочку.")

    if request.method == "POST":
        form = LLMChainForm(request.POST, instance=chain)
        if form.is_valid():
            form.save()
            return redirect('chain_detail', pk=chain.pk)
    else:
        form = LLMChainForm(instance=chain)

    return render(request, 'chain_edit.html', {
        'form': form,
        'chain': chain
    })

def chain_clone(request, pk):
    original_chain = get_object_or_404(LLMChain, pk=pk)

    # Создаем копию, но не сохраняем сразу
    new_chain = LLMChain.objects.get(pk=original_chain.pk)
    new_chain.pk = None  # Сброс ID для создания новой записи
    new_chain._state.db = None  # Очистка состояния БД (на случай многоместного использования)

    # Обновляем поля
    new_chain.name = f"[КОПИЯ] {original_chain.name}"
    new_chain.author = request.user

    # Не копируем связи, если нужно — можно добавить вручную
    # Например: new_chain.use_results = original_chain.use_results

    new_chain.save()

    return redirect('chain_edit', pk=new_chain.pk)

def chain_create(request):
    if request.method == "POST":
        form = LLMChainForm(request.POST)
        if form.is_valid():
            chain = form.save(commit=False)
            chain.author = request.user  # Устанавливаем текущего пользователя как автора
            chain.save()
            return redirect('chain_detail', pk=chain.pk)
    else:
        form = LLMChainForm()

    return render(request, 'chain_create.html', {
        'form': form
    })


def results_list(request):
    run_list = LLMChainRun.objects.select_related('chain', 'model', 'user').prefetch_related('messages').order_by(
        '-created_at')

    paginator = Paginator(run_list, 20)  # 30 записей на страницу
    page_number = request.GET.get('page')

    try:
        runs = paginator.page(page_number)
    except PageNotAnInteger:
        runs = paginator.page(1)
    except EmptyPage:
        runs = paginator.page(paginator.num_pages)

    return render(request, 'results/run_list.html', {'runs': runs})


def result_detail(request, run_id):
    run = get_object_or_404(
        LLMChainRun.objects.select_related('chain', 'model', 'user'),
        pk=run_id
    )
    messages = run.messages.all().order_by('timestamp')
    return render(request, 'results/run_detail.html', {
        'run': run,
        'messages': messages
    })



def load_chain_inputs(request):
    chain_id = request.GET.get('chain')
    program_id = request.GET.get('program')

    if not chain_id or not program_id:
        return HttpResponse("<p class='text-danger'>Выберите цепочку и программу</p>")

    chain = get_object_or_404(LLMChain, id=chain_id)
    program = get_object_or_404(Program, id=program_id)

    # Если цепочка использует результаты другой цепочки — подгружаем список её запусков
    if chain.use_results:
        # Найдём все завершённые runs для этой программы и базовой цепочки
        base_runs = LLMChainRun.objects.filter(
            chain=chain.use_results,
            program=program,
            status="completed"
        ).order_by('-created_at')

        return render(request, 'partials/chain_inputs.html', {
            'result_runs': base_runs,
            'program_id': program.id,
            'model_id': request.GET.get('model'),
            'chain_id': chain.id,
            'use_results_from_chain': chain.use_results
        })

    # Иначе — грузим input-файл
    # input_path = os.path.join(settings.BASE_DIR, chain.input_url.lstrip('/'))
    #
    # if not os.path.exists(input_path):
    #     raise Http404("Файл с входными данными не найден")
    #
    # with open(input_path, 'r', encoding='utf-8') as f:
    #     template_data = json.load(f)

    if chain.inputs:
        template_data = chain.inputs
    else:
        template_data = {}

    filled_data = fill_json_template(template_data, program, None)

    return render(request, 'partials/chain_inputs.html', {
        'inputs': filled_data,
        'program_id': program.id,
        'model_id': request.GET.get('model'),
        'chain_id': chain.id
    })


def load_run_result(request):
    run_id = request.GET.get('run_id') # выбранный run
    chain_run = get_object_or_404(LLMChainRun, id=run_id)
    chain_id = request.GET.get('chain') # нужная цепочка
    chain = get_object_or_404(LLMChain, id=chain_id)



    program = chain_run.program
    input_path = os.path.join(settings.BASE_DIR, chain.input_url.lstrip('/'))

    if not os.path.exists(input_path):

        raise Http404("Файл с входными данными не найден")

    with open(input_path, 'r', encoding='utf-8') as f:
        template_data = json.load(f)

    filled_data = fill_json_template(template_data, program, chain_run)

    return render(request, 'partials/chain_inputs.html', {
        'inputs': filled_data,
        'program_id': program.id,
        'model_id': request.GET.get('model'),
        'chain_id': chain.id
    })


def generate_result(request):
    if request.method != "POST":
        return render(request, "partials/result1.html", {
            "result": {"error": "Метод запроса должен быть POST."}
        })

    # Получение chain и model
    chain = get_object_or_404(LLMChain, pk=request.POST.get('chain'))
    model = get_object_or_404(LLMModel, pk=request.POST.get('model'))
    program = get_object_or_404(Program, pk=request.POST.get('program'))
    # Отбираем входные данные
    excluded = {"program", "chain", "model", "csrfmiddlewaretoken"}
    inputs = {
        key: value for key, value in request.POST.items()
        if key not in excluded
    }

    # Создание LLMChainRun
    chain_run = LLMChainRun.objects.create(
        user=request.user if request.user.is_authenticated else None,
        program=program,
        chain=chain,
        model=model,
        inputs=inputs,
        status="in_progress"
    )

    try:
        # Запуск цепочки
        res = run_flow(chain_run.id, chain.id, model.id, inputs)

        # Сохраняем результат
        chain_run.result = res #unescape_json_string(res)
        chain_run.status = "completed"
        chain_run.save()

    except Exception as e:
        # В случае ошибки
        chain_run.status = "error"
        chain_run.error_message = str(e)
        chain_run.save()

        res = {"error": str(e)}

    return render(request, chain.result_template, {
        'result': res,
        'chain_run_id': chain_run.id
    })


def unescape_json_string(s):
    if isinstance(s, list) and len(s) == 1:
        s = s[0]
    return ast.literal_eval(f"'''{s}'''")



def chain_delete(request, pk):
    chain = get_object_or_404(LLMChain, pk=pk)

    # Проверка прав — только автор может удалить
    if request.user != chain.author:
        raise PermissionDenied("У вас нет прав удалить эту цепочку.")

    if request.method == "POST":
        chain.delete()
        return redirect('chain_list')

    # GET-запрос: отображаем страницу подтверждения
    return render(request, 'chain_confirm_delete.html', {'chain': chain})