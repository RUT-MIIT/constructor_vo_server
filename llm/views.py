import os

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
import json
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404

from constructor_vo_server import settings
from .forms import LoginForm

from llm.models import LLMChain, LLMModel
from programs.models import Program

User = get_user_model()


def get_nested_attr(obj, attr_path):
    attrs = attr_path.split('.')
    for attr in attrs:
        obj = getattr(obj, attr, None)
        if obj is None:
            return None
    return obj

def fill_json_template(template_data, program):
    for field in template_data:
        source = field.get('source')
        value_path = field.get('value')

        if source == "db" and value_path.startswith("program."):
            attr_path = value_path[len("program."):]
            real_value = get_nested_attr(program, attr_path)
            field['value'] = real_value if real_value is not None else field.get('default', "")

        elif source == "input":
            if not field.get('value') and field.get('default'):
                field['value'] = field['default']

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

def load_chain_inputs(request):
    chain_id = request.GET.get('chain')
    program_id = request.GET.get('program')

    if not chain_id or not program_id:
        return HttpResponse("<p class='text-danger'>Выберите цепочку и программу</p>")

    chain = get_object_or_404(LLMChain, id=chain_id)
    program = get_object_or_404(Program, id=program_id)

    # Путь к JSON-шаблону
    input_path = os.path.join(settings.BASE_DIR, chain.input_url.lstrip('/'))
    if not os.path.exists(input_path):
        raise Http404("Файл с входными данными не найден")

    with open(input_path, 'r', encoding='utf-8') as f:
        template_data = json.load(f)

    filled_data = fill_json_template(template_data, program)

    return render(request, 'partials/chain_inputs.html', {
        'inputs': filled_data,
        'program_id': program.id,
        'model_id': request.GET.get('model'),
        'chain_id': chain.id
    })


def generate_result(request):
    # Заглушка
    return HttpResponse("<p><strong>kek</strong> — заглушка результата</p>")