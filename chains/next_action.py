"""
Analyse chain implementation for KTANE bot.
Responsible for analyzing user input and extracting relevant information.
"""
from typing import Type, Dict, Any, Optional

from schemas.schemas import NextAction, BombState, KnownInformation
from prompts.next_action import next_action_prompt

from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1",
    max_tokens=None,
)
json_parser = JsonOutputToolsParser(return_id=True)
parser = PydanticToolsParser(tools=[NextAction])
chain = next_action_prompt | llm.bind_tools(
    tools=[NextAction], tool_choice="NextAction"
)
next_action_chain = chain | parser


if __name__ == "__main__":

    messages = [
        HumanMessage(content="Hey, what should I do? Should I press the button?")
    ]

    user_input = "If the button is red, press it and release it immediatly. If it is blue press it and hold it. Release it when timer has 5 on any position"
    bomb_state = BombState(
        serial_number="4X9BZQ",
        indicators=["SND", "CLR"],
        batteries=3,
        strikes=1
    )

    known_information = KnownInformation(
        known="The button is round",
        unknown="Is SND lit?",
        unsure="False"
    )

    result = next_action_chain.invoke({
        "known_information": known_information,
        "bomb_state": bomb_state,
        "context": user_input,
        "messages": messages
    })

    print(result)