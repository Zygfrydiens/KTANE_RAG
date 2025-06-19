# Additional nodes for KTANE graph
from typing import Dict, Any
from schemas.schemas import (
    NextAction, KnownInformation, KTANEState, BombState, PagesList,
    ModuleStatus, RoutingDecision, FlavouredMessage, RecognitionResult
)
from utils import load_manual_context
from chains.analyse import analyse_chain
from chains.router import router_chain
from chains.next_action import next_action_chain
from chains.find_module import find_module_chain
from chains.flavour import flavour_chain


def router_node(state: KTANEState) -> Dict[str, Any]:
    """Node that routes user input to appropriate specialized nodes"""

    # Use the existing router chain
    result = router_chain.invoke({
        "current_module": state["current_module"],
        "module_description": state["current_module_description"],
        "user_input": state["user_input"],
        "messages": state["messages"]
    })
    updates = {}
    # Extract the RoutingDecision from the result
    routing_decision = None
    for item in result:
        if isinstance(item, RoutingDecision):
            routing_decision = item
            break
    if routing_decision == "recognition":
        print(routing_decision)
        updates["manual_context"] = ""
        updates["current_module"] = ""

    updates["route"] = routing_decision.destination if routing_decision else "defuser"
    return updates

def analyze_input_node(state: KTANEState) -> Dict[str, Any]:
    """Node that analyzes user input and determines next action"""

    # Use your existing chain
    result = analyse_chain.invoke({
        "known_information": state["known_information"],
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


def module_recognition_node(state: KTANEState) -> Dict[str, Any]:
    """Node that identifies bomb modules based on user descriptions"""

    # Use the existing find_module_chain
    result = find_module_chain.invoke({
        "known_information": state["known_information"].known,
        "descriptions": state["module_descriptions"],
        "user_input": state["user_input"],
        "messages": state["messages"]
    })

    # Extract the RecognitionResult from the result
    recognition_result = None
    for item in result:
        if isinstance(item, RecognitionResult):
            recognition_result = item
            break

    if not recognition_result:
        return {}

    # Update known information
    updates = {
        "known_information": recognition_result.known_information,
        "current_module": recognition_result.module_recognition.module_name,
        "current_module_description": recognition_result.module_recognition.module_description
    }

    # If we got a PagesList (module identified), load the manual context
    if recognition_result.module_recognition:
        manual_context = load_manual_context(
            recognition_result.module_recognition.page_number,
            state["enhanced_manual_pages"]
        )
        updates["manual_context"] = manual_context

    return updates


def defuser_assistant_node(state: KTANEState) -> Dict[str, Any]:
    """Node that provides defusal instructions using next_action_chain"""

    # Use the existing next_action_chain
    result = next_action_chain.invoke({
        "known_information": state["known_information"],
        "bomb_state": state["bomb_state"],
        "context": state["manual_context"],
        "messages": state["messages"],
        "user_input": state["user_input"]
    })

    # Extract the NextAction from the result
    next_action_update = None
    for item in result:
        if isinstance(item, NextAction):
            next_action_update = item
            break

    return {
        "next_action": next_action_update or state.get("next_action")
    }


def faq_answerer_node(state: KTANEState) -> Dict[str, Any]:
    """Node that handles FAQ questions about bomb mechanics"""

    # For FAQ, we can create a simple response or use a dedicated chain
    # This is a placeholder - you might want to implement FAQ logic

    # Simple FAQ responses based on common questions
    user_input = state["user_input"].lower()

    if "serial" in user_input and "look" in user_input:
        faq_response = "The serial number is printed on the side of the bomb casing, usually near the bottom."
    elif "indicator" in user_input and ("where" in user_input or "find" in user_input):
        faq_response = "Indicators are small displays with 3-letter codes, usually found on the top or sides of the bomb."
    elif "batter" in user_input and ("where" in user_input or "find" in user_input):
        faq_response = "Batteries are typically in compartments on the back or sides of the bomb."
    elif "wire" in user_input and "cut" in user_input:
        faq_response = "To cut a wire, use wire cutters and cut the specific wire mentioned in the instructions."
    else:
        faq_response = "I can help with bomb defusal questions. Ask about serial numbers, indicators, batteries, or general module mechanics."

    # Create a NextAction with the FAQ response
    faq_action = NextAction(action=faq_response)

    return {
        "next_action": faq_action
    }


def create_flavoured_message_node(state: KTANEState) -> Dict[str, Any]:
    """Node that adds personality to the response using flavour_chain"""

    # Determine the type of message based on what we have
    next_action = state.get("next_action")
    known_info = state.get("known_information")

    if not next_action:
        return {}

    # Determine message type
    message_type = "next_action"  # default

    if known_info and known_info.unknown.strip():
        message_type = "unknowns"
    elif "serial" in next_action.action.lower() or "indicator" in next_action.action.lower():
        message_type = "faq"

    # Use the existing flavour_chain
    result = flavour_chain.invoke({
        "type": message_type,
        "input": next_action.action,
        "messages": state["messages"]
    })

    # Extract the FlavouredMessage from the result
    flavoured_message = None
    for item in result:
        if isinstance(item, FlavouredMessage):
            flavoured_message = item
            break

    return {
        "flavoured_message": flavoured_message.message if flavoured_message else next_action.action,
    }


# Optional: If you want to combine some existing nodes with new functionality
def enhanced_analyze_input_node(state: KTANEState) -> Dict[str, Any]:
    """Enhanced version of analyze_input_node that also handles routing"""

    # First do the original analysis (if you have analyse_chain)
    # Then add routing logic

    # For now, let's just route based on simple logic
    routing_result = router_node(state)

    return {
        **routing_result,
        # Add any other analysis results here
    }