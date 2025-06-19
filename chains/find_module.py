"""
Analyse chain implementation for KTANE bot.
Responsible for analyzing user input and extracting relevant information.
"""
from typing import Type, Dict, Any, Optional
import json
from pydantic import BaseModel, Field, parse_obj_as
from schemas.schemas import PagesList, KnownInformation, ModuleRecognition, RecognitionResult
from prompts.find_module import find_module_prompt

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
parser = PydanticToolsParser(tools=[RecognitionResult])

chain = find_module_prompt | llm.bind_tools(
    tools=[RecognitionResult]
)
find_module_chain = chain | parser


if __name__ == "__main__":
    with open("../manual_images/recognized_modules.json", "r", encoding="utf-8") as f:
        loaded = json.load(f)
    modules: list[ModuleRecognition] = parse_obj_as(list[ModuleRecognition], loaded)

    # 3. Use the loaded models
    descriptions = ""
    for m in modules:
        descriptions += f"Page {m.page_number}: {m.module_name} – {m.module_description}\n"

    messages = [
        HumanMessage(content="The module has 3 wires"),
        HumanMessage(content="I am pushing the button and releasing"),
        HumanMessage(content="This is corrent now I see new module"),
        HumanMessage(content="The module has 3 wires"),
    ]

    user_input = messages[-1]

    known_information = KnownInformation(
        known="3 wires.",
        unknown="",
        unsure=""
    )

    result = find_module_chain.invoke({
        "known_information": known_information.known,
        "descriptions": descriptions,
        "user_input": user_input,
        "messages": messages
    })

    print(result)