from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

analyse_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a support specialist in *Keep Talking and Nobody Explodes*.

**Task:** Analyse the conversation and update bomb state.

Current bomb state (JSON):
{bomb_state}

Known Information (JSON):
{known_information}

Current user input:
{user_input}

Steps:
1. Extract which facts about the CURRENT module are already known. Input things given by the user and state which will help indentify current module, find context from the manual and defuse it.
2. State exactly which facts are missing and prevent progress.
3. If the module itself is unknown, say so in `unknown`.
4. Assume the user can make mistakes. Assume that the context given can be wrong. If something is unsure and contradictory, note it as unsure.

Return **one JSON object** of type `KnownInformation` *and* **one JSON object** of type 'BombState'""",
                ),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Return the `KnownInformation` and 'BombState' object using the required format.",
                ),
            ]
        )