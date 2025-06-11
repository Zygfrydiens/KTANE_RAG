from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field


class BombState(BaseModel):
    """Persisted across turns; anything the agent needs every cycle."""

    """manual_context: Optional[str] = Field(
        None,
        description="Cached excerpt from the manual relevant to the CURRENT module. "
                    "If None, the agent should retrieve it via RAG."
    )"""
    serial_number: Optional[str] = Field(
        None,
        description="Serial printed on the bomb (e.g. '24TXYZ'). None if not yet known."
    )
    indicators: Optional[List[str]] = Field(
        default_factory=list,
        description="Labels of indicators already reported by the defuser."
    )
    batteries: Optional[int] = Field(
        None,
        ge=0,
        description="Total battery count. None if not yet known."
    )
    strikes: Optional[int] = Field(
        0,
        ge=0,
        le=2,
        description="Current strike count (0-2)."
    )


class KnownInformation(BaseModel):
    """
    Extends BombState with the agent's introspection about what it already knows
    and what it still has to ask for.
    """

    known: str = Field(
        "",
        description="Facts already gathered that about current module."
    )
    unknown: str = Field(
        "",
        description="Missing facts the defuser still needs to supply about current module."
    )
    unsure: str = Field(
        "",
        description="Unsure about module? True or False"
    )


class ManualContext(BaseModel):
    """Raw chunk returned by RAG for a specific module."""

    module_name: str = Field(
        ...,
        description="Exact name of the bomb module this context belongs to."
    )
    text: str = Field(
        ...,
        description="Verbatim rules excerpt needed to reason about the module."
    )


class NextAction(BaseModel):
    """
    Cold, flavour-free instruction or question for the defuser.
    Example: 'What is the first wire from the top?', "Is there a serial port? It should be somewhere on the device, looks like an input with two rows of holes, one row has 9 holes, second 8"  or  'Press and HOLD the red button.'
    """

    action: str = Field(
        ...,
        description="Single, unambiguous instruction or question."
    )

class FlavouredMessage(BaseModel):
    """User-facing message with personality (one sentence, max ~30 words)."""
    message: str = Field(
        ...,
        description="Concise line addressed to the defuser, already in-character."
    )

class PagesList(BaseModel):
    """List of pages to download contex from"""
    message: List[int] = Field(
        default_factory=list,
        description="A list of page numbers from the defusal manual."
    )

class ModuleRecognition(BaseModel):
    """
    Holds the essential information needed to identify a bomb module
    in Keep Talking and Nobody Explodes.
    """
    module_name: str = Field(
        ...,
        description="Exact, official name of the bomb module."
    )
    module_description: str = Field(
        ...,
        description=(
            "Concise description of the module’s stable visual features; "
        )
    )
    page_number: int = Field(
        ...,
        description="Manual page number from which this context was extracted."
    )

class ModuleStatus(BaseModel):
    """Status of current module"""
    is_completed: bool = Field(description="Whether the current module has been completed")
    completion_reason: str = Field(description="Why this module is considered complete")


class KTANEState(TypedDict):
    # Core bomb information
    bomb_state: BombState
    known_information: KnownInformation

    # Current interaction
    user_input: str
    messages: List[dict]  # Chat history

    # Manual context (when retrieved)
    manual_context: Optional[str]

    # Current action to take
    next_action: Optional[NextAction]
    module_descriptions: str
    enhanced_manual_pages: List

    retrieve_data_retries: int
