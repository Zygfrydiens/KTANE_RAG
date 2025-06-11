# nodes.py
from typing import Dict, Any
from schemas.schemas import NextAction, KnownInformation, KTANEState, BombState, PagesList
from utils import load_manual_context
from chains.analyse import analyse_chain
from chains.next_action import next_action_chain
from chains.find_module import find_module_chain


def analyze_input_node(state: KTANEState) -> Dict[str, Any]:
    """Node that analyzes user input and determines next action"""

    # Use your existing chain
    result = analyse_chain.invoke({
        "known_information": state["known_information"],
        "bomb_state": state["bomb_state"],
        "user_input": state["user_input"],
        "messages": state['messages']
    })

    # Separate the results by type
    bomb_state_update = None
    known_info_update = None

    for item in result:
        if isinstance(item, BombState):
            bomb_state_update = item
        elif isinstance(item, KnownInformation):
            known_info_update = item
    return {
        "bomb_state": bomb_state_update or state["bomb_state"],
        "known_information": known_info_update or state["known_information"]
    }


def next_action_node(state: KTANEState) -> Dict[str, Any]:
    """Node that determines the next action/instruction for the defuser"""

    # Use your existing chain
    result = next_action_chain.invoke({
        "known_information": state["known_information"],
        "bomb_state": state["bomb_state"],
        "context": state["user_input"],
        "messages": state["messages"]
    })

    # Extract the NextAction from the result
    next_action_update = None

    for item in result:
        if isinstance(item, NextAction):
            next_action_update = item

    return {
        "next_action": next_action_update or state["next_action"]
    }


def retrieve_data_node(state: KTANEState) -> Dict[str, Any]:
    """Node that retrieves manual context or updates known information"""

    # Increment retry counter
    retry_count = state.get("retrieve_data_retries", 0) + 1

    # Use your existing chain
    result = find_module_chain.invoke({
        "known_information": state["known_information"].known,
        "descriptions": state["module_descriptions"]
    })

    # Separate the results by type
    known_info_update = None
    pages_list_update = None

    for item in result:
        if isinstance(item, KnownInformation):
            known_info_update = item
        elif isinstance(item, PagesList):
            pages_list_update = item

    # If we got a PagesList, load the manual context
    if pages_list_update:
        manual_context = load_manual_context(pages_list_update, state["enhanced_manual_pages"])
        return {
            "manual_context": manual_context,
            "retrieve_data_retries": retry_count
        }

    # Otherwise, return updated known information
    return {
        "known_information": known_info_update or state["known_information"],
        "retrieve_data_retries": retry_count
    }

