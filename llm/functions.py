import json
import ast


def idea(inputs, **kwargs):
    chain_result = inputs.get("chain_result", [])
    step_result = chain_result[-1] if chain_result else {}
    result = step_result.get("result", {})
    concept = result.get("program_concept_summary")


    # Извлекаем части
    parts = [
        concept.get("program_core_focus", ""),
        concept.get("key_product_types_summary", ""),
        concept.get("professional_activity_areas", ""),
        concept.get("regulatory_context_summary", ""),
        concept.get("target_professional_profile_summary", ""),
    ]

    # Возвращаем объединённый текст
    return "\n\n".join([p.strip() for p in parts if p.strip()])


def nsi_products(inputs):

    chain_result = inputs.get("chain_result", [])
    step_result = chain_result[-2] if chain_result else {}
    result = step_result.get("result", {})
    mapping = result.get("product_nsi_mapping", [])

    if not mapping:
        return "Нет данных о соответствии продуктов нормативной документации."

    parts = []

    for product in mapping:
        product_name = product.get("product_name", "Без названия продукта")
        docs = product.get("relevant_nsi", [])

        product_text = [f"{product_name}:\n"]

        for doc in docs:
            title = doc.get("document_title", "Название документа неизвестно")
            org = doc.get("organization", "Организация неизвестна")
            year = doc.get("year", "Год неизвестен")
            level = doc.get("level", "Уровень не указан")
            purpose = doc.get("purpose", "Описание отсутствует")

            doc_text = (
                f"- {title} ({org}, {year}, {level})\n"
                f"  {purpose}"
            )
            product_text.append(doc_text)

        parts.append("\n".join(product_text))

    return "\n\n".join(parts)


def context(inputs):
    chain_result = inputs.get("chain_result", [])
    step_result = chain_result[0] if chain_result else {}

    params = step_result.get("result", {}).get("program_parameters", {})

    if not params:
        return "Нет данных о параметрах программы."

    text = []
    #text.append(f"Профиль программы: {params.get('program_profile', 'не указан')}")
    #text.append(f"Код направления: {params.get('direction_code', 'не указан')}\n")

    text.append("Целевая направленность подготовки:")
    text.append(params.get('target_training_description', 'Описание отсутствует.'))
    text.append("")

    text.append("Входные компетенции:")
    text.append(params.get('entry_competencies_summary', 'Информация отсутствует.'))
    text.append("")

    text.append("Выходные компетенции:")
    text.append(params.get('exit_competencies_summary', 'Информация отсутствует.'))
    text.append("")

    text.append("Целевые должности выпускников:")
    for position in params.get('target_positions', []):
        text.append(f"- {position}")
    text.append("")

    text.append("Потенциальные работодатели:")
    for employer in params.get('potential_employers', []):
        text.append(f"- {employer}")
    text.append("")

    text.append("Отраслевой контекст:")
    text.append(params.get('industry_context', 'Информация отсутствует.'))

    return "\n".join(text)
