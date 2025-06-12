# graph.py
from langgraph.graph import StateGraph, END
from nodes import *


def build_ktane_graph():
    # Create the graph
    builder = StateGraph(KTANEState)

    # Add nodes
    builder.add_node("check_completion", check_completion_node)
    builder.add_node("analyze_input", analyze_input_node)
    builder.add_node("retrieve_data", retrieve_data_node)
    builder.add_node("generate_next_action", next_action_node)

    # Set entry point
    builder.set_entry_point("analyze_input")

    # Define the decision logic
    def should_retrieve_data(state: KTANEState) -> str:
        """Run retrieve_data only when context is empty AND there's unknown info (max 3 retries)"""

        # Get current retry count (default to 0 if not present)
        retry_count = state.get("retrieve_data_retries", 0)

        # Check if we've exceeded max retries
        if retry_count >= 3:
            return "generate_next_action"

        # Original logic
        manual_context_empty = not state.get("manual_context") or state["manual_context"] == ""
        has_unknown_info = state["known_information"].unknown.strip() != ""

        if manual_context_empty and has_unknown_info:
            return "retrieve_data"
        else:
            return "generate_next_action"

    # Add edges
    builder.add_conditional_edges("analyze_input", should_retrieve_data)
    builder.add_edge("retrieve_data", "generate_next_action")
    builder.add_edge("generate_next_action", END)

    return builder.compile()


# Create the graph
ktane_graph = build_ktane_graph()