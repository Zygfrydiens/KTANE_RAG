"""
Flavour the message to the user
"""
from typing import Type, Dict, Any, Optional, List

from schemas.schemas import BombState, KnownInformation, RoutingDecision, FlavouredMessage
from prompts.flavour import flavour_prompt

from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1-nano",
    max_tokens=None,
)
json_parser = JsonOutputToolsParser(return_id=True)
parser = PydanticToolsParser(tools=[FlavouredMessage])
chain = flavour_prompt | llm.bind_tools(
    tools=[FlavouredMessage]
)
flavour_chain = chain | parser


if __name__ == "__main__":

    if __name__ == "__main__":
        # previous conversation (very short for demo)
        messages: List[HumanMessage] = [
            HumanMessage(content="The serial number is 4X9BZQ"),
            HumanMessage(content="The wires are red, blue and white")
        ]

        # we haven’t identified any module yet
        current_module: Optional[str] = None

        # invoke the chain
        result = flavour_chain.invoke(
            {
                "type": "unknowns",
                "input": "Number of batteries",
                "messages": messages
            }
        )

        print(result)