from graph import ktane_graph
from schemas.schemas import *
from utils import load_enhanced_pages, load_module_descriptions


def run_ktane_chat():
    """Interactive chat loop for KTANE bomb defusal"""

    # Load resources once
    print("🔧 Loading KTANE manual and modules...")
    enhanced_pages = load_enhanced_pages()
    descriptions = load_module_descriptions()

    # Initialize state
    state = {
        "bomb_state": BombState(),
        "known_information": KnownInformation(
            known="",
            unknown="",
            unsure="False"
        ),
        "user_input": "",
        "messages": [],
        "manual_context": "",
        "next_action": None,
        "module_descriptions": descriptions,
        "enhanced_manual_pages": enhanced_pages,
        "retrieve_data_retries": 0
    }

    print("💣 KTANE Bomb Defusal Assistant")
    print("Type 'quit' to exit, 'reset' to start over")
    print("-" * 50)

    while True:
        # Get user input
        user_input = input("\n🔍 Describe what you see: ").strip()

        # Handle special commands
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Stay safe out there!")
            break
        elif user_input.lower() == 'reset':
            print("🔄 Resetting bomb state...")
            state = {
                "bomb_state": BombState(),
                "known_information": KnownInformation(known="", unknown="", unsure="False"),
                "user_input": "",
                "messages": [],
                "manual_context": "",
                "next_action": None,
                "module_descriptions": descriptions,
                "enhanced_manual_pages": enhanced_pages,
                "retrieve_data_retries": 0
            }
            continue
        elif user_input == '':
            continue

        # Add user message to conversation history
        user_message = {"role": "user", "content": user_input}
        state["messages"].append(user_message)
        state["user_input"] = user_input

        try:
            # Process through the graph
            print("🤖 Analyzing...")
            result = ktane_graph.invoke(state)

            # Update state with results (important for memory!)
            state.update(result)

            # Display the response
            if result.get("next_action"):
                print(f"🎯 Next Action: {result['next_action'].action}")

            # Optional: Show current knowledge state
            if result["known_information"].known:
                print(f"✅ Known: {result['known_information'].known}")
            if result["known_information"].unknown:
                print(f"❓ Unknown: {result['known_information'].unknown}")

        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with different input.")

        # Reset retry counter for next input
        state["retrieve_data_retries"] = 0


# Run the chat
if __name__ == "__main__":
    run_ktane_chat()