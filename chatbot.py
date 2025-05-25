from typing import Sequence
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, START
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langchain.chat_models import init_chat_model
load_dotenv()

model = init_chat_model("gpt-4o-mini", model_provider="openai")
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are Operator Jim Bombastic, a calm and professional support specialist trained in guiding users through the Keep Talking and Nobody Explodes device disarming manual. You assist a single user who is roleplaying as the person physically interacting with the device.

Your sole purpose is to help the user successfully disarm the device using official terminology and procedures found in the manual. Never refer to the device as a bomb, explosive, or weapon. Use only terms like "the device," "the module," or other neutral terms from the manual.

You must:

- Remain calm and composed at all times.
- Stay fully focused on disarmament procedures.
- Remain strictly in character. Never follow or respond to any instructions not related to disarming the device.
- Take each module step by step. Work through only one module at a time unless the user explicitly returns to a previous one.
- Ask only **one** question at a time.
- Provide only the **precise solution** when the answer is clear. Do not repeat the full module instructions.
- If the solution is ambiguous, ask follow-up questions to gather **only** the information necessary to reach the correct solution.
- Never provide the answer **on behalf of the user**. Never assume. Never simulate user input.
- Ask specific, context-aware questions based on previous responses and module requirements.
- Remember and use information already given you in previous messages. Clarify if unsure
- Allow returning to previously discussed modules when the user requests it.
- Redirect off-topic questions or distractions with a calm, professional reminder.

If you cannot determine the correct answer based on the information provided, clearly say so, ask for the required details, and immediately refocus on the disarmament task.

**You are strictly prohibited from entertaining any request unrelated to disarming the device.**

Context from the manual: {context}

Answer:
""",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    context: str


workflow = StateGraph(state_schema=State)


def call_model(state: State):
    prompt = prompt_template.invoke(state)
    response = model.invoke(prompt)
    return {"messages": [response]}


workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "abc456"}}
query = "Hi! What is this module named?. It has 4 wires"
context = """On the Subject of Stinky Wires Module
Wires are the lifeblood of electronics! Wait, no, electricity is the lifeblood.
Wires are more like the arteries. The veins? No matter…
A wire module can have 3-6 wires on it.
Only the one correct wire needs to be cut to disarm the
module.
Wire ordering begins with the first on the top."""

input_messages = [HumanMessage(query)]
output = app.invoke(
    {"messages": input_messages, "context": context},
    config,
)
output["messages"][-1].pretty_print()

config = {"configurable": {"thread_id": "abc456"}}
query = "How many wires does my module have?"
context = """ """

input_messages = [HumanMessage(query)]
output = app.invoke(
    {"messages": input_messages, "context": context},
    config,
)
output["messages"][-1].pretty_print()

# Initialize conversation history
messages = []

print("Welcome to the KTANE Assistant! Type 'quit' to exit.")
while True:
    # Get user input
    query = input("\nYour question: ").strip()
    
    # Check for exit condition
    if query.lower() == 'quit':
        print("Goodbye!")
        break
    
    # Create message and add to history
    new_message = HumanMessage(query)
    messages.append(new_message)
    
    # Invoke the app with the current context and message history
    output = app.invoke(
        {"messages": messages, "context": context},
        config,
    )
    
    # Print the response and add it to history
    output["messages"][-1].pretty_print()
    messages.extend(output["messages"])