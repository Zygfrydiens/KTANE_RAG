"""
Analyse chain implementation for KTANE bot.
Responsible for analyzing user input and extracting relevant information.
"""
from typing import Type, Dict, Any, Optional

from schemas.schemas import BombState, KnownInformation
from prompts.quick_response import quick_response_prompt

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1",
    max_tokens=None,
    temperature=1,
)

quick_response_chain = quick_response_prompt | llm