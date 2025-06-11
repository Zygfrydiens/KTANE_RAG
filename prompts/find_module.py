from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

find_module_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a support specialist in *Keep Talking and Nobody Explodes*.

**Task:** 
*Check if the known_information fits more than one module*. If yes, update unknown field with information that will help find the correct module.
Otherwise, return the PageList of a module the user sees based on the known information.

Known Information:
{known_information}

Descriptions of modules:
{descriptions}
""",
                ),
                (
                    "system",
                    "Return the `KnownInformation` or 'PagesList' object using the required format",
                ),
            ]
        )