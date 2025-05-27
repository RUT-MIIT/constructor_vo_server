import os
from openai import OpenAI
from llm.models import LLMMessage
from dotenv import load_dotenv
load_dotenv()

def call_llm(messages):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    r = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages
    )
    return r.choices[0].message.content


def log_llm_message(*, run, message_type, message_text):
    """
    Логирует одно сообщение (user, assistant, system и т.п.) в LLMMessage.

    :param run: объект LLMChainRun (обязателен)
    :param message_type: 'user', 'assistant', 'system', 'tool', 'raw' — тип сообщения
    :param message_text: текст сообщения
    """
    try:
        LLMMessage.objects.create(
            llm_chain_run=run,
            type=message_type,
            message=message_text
        )

    except Exception as e:
        print(f"[ERROR] Ошибка при сохранении LLMMessage: {e}")

# Example usage
if __name__ == "__main__":
    print(call_llm("Tell me a short joke"))