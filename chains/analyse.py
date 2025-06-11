"""
Analyse chain implementation for KTANE bot.
Responsible for analyzing user input and extracting relevant information.
"""
from typing import Type, Dict, Any, Optional

from schemas.schemas import BombState, KnownInformation
from prompts.analyse import analyse_prompt

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
parser = PydanticToolsParser(tools=[BombState, KnownInformation])
chain = analyse_prompt | llm.bind_tools(
    tools=[BombState, KnownInformation]
)
analyse_chain = chain | parser


if __name__ == "__main__":

    messages = [
        HumanMessage(content="The serial number is 4X9BZQ")
    ]

    user_input = [
        HumanMessage(content="The wires are horizontal!")
    ]
    bomb_state = BombState(
        serial_number="4X9BZQ",
        indicators=["SND", "CLR"],
        batteries=3,
        strikes=1
    )

    known_information = KnownInformation(
        known="The module has 3 wires and the last one is red.",
        unknown="Are wires horizontal or vertical?",
        unsure="False"
    )

    result = analyse_chain.invoke({
        "known_information": known_information,
        "bomb_state": bomb_state,
        "user_input": user_input,
    })

    print(result)