from dataclasses import dataclass


@dataclass
class MemoryItem:
    content: str
    tags: list[str]


LONG_TERM_MEMORY = [
    MemoryItem(
        content="Student requested a two-day project extension.",
        tags=["student", "project", "extension"]
    ),
    MemoryItem(
        content="Faculty member replied asking the student to submit the revised report by Friday.",
        tags=["student", "project", "deadline"]
    ),
    MemoryItem(
        content="Research collaborator discussed scheduling a meeting for a joint paper.",
        tags=["research", "meeting", "collaborator"]
    )
]


def store_memory(content: str, tags: list[str]):
    """
    Stores information in long-term memory.
    """

    LONG_TERM_MEMORY.append(
        MemoryItem(
            content=content,
            tags=tags
        )
    )


def retrieve_by_tag(tag: str) -> list[MemoryItem]:
    """
    Retrieves memories containing the requested tag.
    """

    results = []

    for memory in LONG_TERM_MEMORY:
        if tag in memory.tags:
            results.append(memory)

    return results



def retrieve_by_similarity(query: str) -> list[MemoryItem]:
    """
    Retrieves memories that share important words with the query.
    """

    query_words = set(query.lower().split())

    scored_results = []

    for memory in LONG_TERM_MEMORY:
        memory_words = set(memory.content.lower().split())

        common_words = query_words.intersection(memory_words)

        if common_words:
            score = len(common_words)
            scored_results.append((score, memory))

    scored_results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [memory for score, memory in scored_results]


@dataclass
class SessionState:
    run_id: str
    user_request: str
    current_plan: str | None = None
    current_email: str | None = None
    tool_results: list = None

    def __post_init__(self):
        if self.tool_results is None:
            self.tool_results = []
            
def get_grounding_context(
    sender: str,
    subject: str = "",
    body: str = ""
) -> list[MemoryItem]:

    text = f"{sender} {subject} {body}".lower()

    results = []

    for memory in LONG_TERM_MEMORY:
        for tag in memory.tags:
            if tag.lower() in text:
                results.append(memory)
                break

    return results