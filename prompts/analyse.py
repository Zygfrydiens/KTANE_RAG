from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

analyse_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a support specialist in *Keep Talking and Nobody Explodes*.

**Task:** Analyse the conversation and update known information about the current module.


Known Information (JSON):
{known_information}

Current user input:
{user_input}

Extract which facts about the CURRENT module are already known. Input things given by the user and state which will help indentify current module, find context from the manual and defuse it.

Return **one JSON object** of type `KnownInformation`""",
                ),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Return the `KnownInformation` object using the required format.",
                ),
            ]
        )