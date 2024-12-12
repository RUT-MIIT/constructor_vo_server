import os

from django.http import HttpResponse
from django.shortcuts import render

from docx import Document
from programs.models import Product, Nsi, Program
from docxtpl import DocxTemplate



def export_data(request, program_id):
    rd = export_rd(program_id)
    return rd

def export_dataset(program_id):
    # Создание нового документа
    doc = Document('export/templates/base.docx')
    program = Program.objects.get(id=program_id)
    # Получаем все продукты
    products = Product.objects.filter(program_id=program_id)

    p = doc.add_paragraph()
    p.add_run(f"Датасет программы «{program.profile}»").bold = True
    doc.add_paragraph(f"Уровень образования: {program.level_id.name}")
    doc.add_paragraph(f"Направление: {program.direction_id.code} {program.direction_id.name}")
    doc.add_paragraph()

    # Для каждого продукта добавляем в документ его название и список Nsi
    for product in products:
        # Добавляем название продукта жирным
        p = doc.add_paragraph()
        p.add_run(product.name).bold = True
        # Добавляем описание
        doc.add_paragraph(product.description)
        # Получаем связанные Nsi и добавляем их в список
        nsi_list = product.nsis.all()
        if nsi_list:
            # Добавляем заголовок для списка Nsi
            doc.add_paragraph("Нормативные акты :")

            # Перечисляем все связанные Nsi
            for nsi in nsi_list:
                doc.add_paragraph(nsi.nsiFullName, style='marked_list')

        # Добавляем пустую строку после каждого продукта
        doc.add_paragraph()

    # Сохраняем документ
    directory = os.path.join(f"export/programs/{program_id}")
    if not os.path.exists(directory):
        os.makedirs(directory)

    url = f"export/programs/{program_id}/Датасет.docx"
    doc.save(url)


def export_rd(program_id):
    # Создание нового документа

    program = Program.objects.get(id=program_id)
    # Получаем все продукты
    products = Product.objects.filter(program_id=program_id)

    # Проверяем директорию
    directory = os.path.join(f"export/programs/{program_id}/Реконструкция деятельности")
    if not os.path.exists(directory):
        os.makedirs(directory)

    for product in products:
        doc = Document('export/templates/base.docx')
        p = doc.add_paragraph("ДЕКОМПОЗИЦИЯ ЖИЗНЕННОГО ЦИКЛА", style='bold_centered')
        run = p.add_run()
        run.add_break()
        run = p.add_run(f"продукта «{product.name}»")

        url = f"export/programs/{program_id}/Реконструкция деятельности/{product.name}.docx"
        doc.save(url)

        p = doc.add_paragraph()
        p.add_run(f"Датасет программы «{program.profile}»").bold = True

    return "KEK"






