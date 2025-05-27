import os
import re

import django

# Настройка Django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'constructor_vo_server.settings')
# django.setup()

from .flow import create_chain_flow
from llm.models import LLMChain, LLMModel, LLMChainRun
from django.shortcuts import get_object_or_404


def run_flow(chain_run_id, chain_id, model_id,inputs):
    chain = get_object_or_404(LLMChain, pk=chain_id)
    model_obj = get_object_or_404(LLMModel, pk=model_id)
    chain_run_obj = get_object_or_404(LLMChainRun, pk=chain_run_id)

    model = {
        "model_name": model_obj.model_name,
        "api_url": model_obj.api_url,
        "api_key": model_obj.api_key,
    }
    if chain.prompt:
        markdown_text = chain.prompt
    #with open(chain.file_url, 'r', encoding='utf-8') as file:
    #    markdown_text = file.read()


    steps = re.findall(r"<step>.*?</step>", markdown_text, re.DOTALL)
    shared = {"main_prompt": markdown_text,"steps_count": len(steps), "model": model, "inputs": inputs,
              "chain_run": chain_run_obj,"current_step": 1,"messages":[], "results": []}


    print(f"\n=== Starting GEN\n")
    #
    # # Run the flow
    flow = create_chain_flow(len(steps))
    flow.run(shared)
    #
    # # Output summary
    # print("\n=== Workflow Completed ===\n")
    # print(f"Topic: {shared['topic']}")
    # print(f"Outline Length: {len(shared['outline'])} characters")
    # print(f"Draft Length: {len(shared['draft'])} characters")
    # print(f"Final Article Length: {len(shared['final_article'])} characters")

    return shared["results"]


if __name__ == "__main__":
    chain_id = 1
    model_id = 2
    inputs = {}
    run_flow(chain_id,model_id,inputs)