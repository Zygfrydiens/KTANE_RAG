"""
Analyse chain implementation for KTANE bot.
Responsible for analyzing user input and extracting relevant information.
"""
from typing import Type, Dict, Any, Optional, List

from schemas.schemas import BombState, KnownInformation, RoutingDecision
from prompts.router import routing_prompt

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
parser = PydanticToolsParser(tools=[RoutingDecision])
chain = routing_prompt | llm.bind_tools(
    tools=[RoutingDecision]
)
router_chain = chain | parser


if __name__ == "__main__":

    if __name__ == "__main__":
        # previous conversation (very short for demo)
        messages: List[HumanMessage] = [
            HumanMessage(content="The serial number is 4X9BZQ"),
            HumanMessage(content="Do you like me??")
        ]

        # brand-new user utterance
        user_input = messages[-1]

        # we haven’t identified any module yet
        current_module: Optional[str] = None

        # invoke the chain
        result: RoutingDecision = router_chain.invoke(
            {
                "current_module": current_module,
                "user_input": user_input,
                "messages": messages,
            }
        )

        print(result)  # e.g. RoutingDecision(destination='recognition')
        print("→ next node:", result[0].destination)