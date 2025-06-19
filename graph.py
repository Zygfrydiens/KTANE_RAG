# updated_graph.py
from langgraph.graph import StateGraph, END, START
from nodes import *


def build_ktane_graph():
    """Build the KTANE graph according to the architecture diagram"""

    # Create the graph
    builder = StateGraph(KTANEState)

    # Add all nodes
    builder.add_node("router", router_node)
    builder.add_node("analyse", analyze_input_node)
    builder.add_node("module_recognition", module_recognition_node)
    builder.add_node("defuser_assistant", defuser_assistant_node)
    builder.add_node("create_flavoured_message", create_flavoured_message_node)


    # Define routing logic based on router decision
    def route_after_router(state: KTANEState) -> str:
        """Route to the appropriate node based on router decision"""
        routing_decision = state["route"]
        print(routing_decision)
        if state["current_module"] == "" or routing_decision == "recognition":
            return "module_recognition"
        elif routing_decision == "defuser":
            return "defuser_assistant"

    # Define routing after module recognition
    def route_after_recognition(state: KTANEState) -> str:
        """Route to defuser if module was identified, otherwise create message"""
        if state.get("manual_context") and state["manual_context"].strip():
            return "defuser_assistant"
        else:
            return "create_flavoured_message"

    # Add edges following the architecture diagram
    builder.add_edge(START, "analyse")
    builder.add_edge(START, "router")
    builder.add_conditional_edges("router", route_after_router)
    builder.add_conditional_edges("module_recognition", route_after_recognition)

    builder.add_edge("defuser_assistant", "create_flavoured_message")

    builder.add_edge("create_flavoured_message", END)

    return builder.compile()

# Create both graph versions
ktane_graph = build_ktane_graph()
