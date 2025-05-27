from pocketflow import Flow
from .nodes import NoticePrompt, SetInputs, MakeStep


def create_chain_flow(steps_count):

    # Create node instances
    notice_node = NoticePrompt()
    input_node = SetInputs()
    step_nodes = []
    current_node = notice_node >> input_node

    # Создание и последовательное соединение step_n
    for step in range(1, steps_count + 1):
        step_node = MakeStep(step)
        current_node = current_node >> step_node

    # Create flow
    chain_flow = Flow(start=notice_node)

    return chain_flow