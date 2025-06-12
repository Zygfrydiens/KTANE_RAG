"""
Module status check chain implementation for KTANE bot.
Responsible for detecting if user has completed a module based on their input.
"""
from typing import Type, Dict, Any, Optional

from schemas.schemas import ModuleStatus
from prompts.module_status_check import module_status_check_prompt
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()

# Create the LLM and parsers
llm = ChatOpenAI(
    model="gpt-4.1",
    max_tokens=None,
    temperature=0.7
)

json_parser = JsonOutputToolsParser(return_id=True)
parser = PydanticToolsParser(tools=[ModuleStatus])

# Create the chain
chain = module_status_check_prompt | llm.bind_tools(tools=[ModuleStatus])
module_status_check_chain = chain | parser


if __name__ == "__main__":
    # Test the chain
    messages = [
        HumanMessage(content="I've finished last one. The light is green and module is solved. I now see wires"),
        HumanMessage(content="Cut last one!"),
        HumanMessage(content="Done, what now?"),
        HumanMessage(content="Cut red one!"),
    ]

    user_input = "Done! Lets go to the next module. Now I see 4 buttons!"

    result = module_status_check_chain.invoke({
        "user_input": user_input,
        "messages": messages
    })

    print(result)