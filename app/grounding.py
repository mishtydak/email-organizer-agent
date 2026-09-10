from dataclasses import dataclass


@dataclass
class Evidence:
    source: str
    content: str
    relevance: float


def retrieve_evidence(
    email,
    memory_items
):
    text = (
        f"{email.sender} "
        f"{email.subject} "
        f"{email.body}"
    ).lower()

    evidence = []

    for memory in memory_items:
        score = 0

        for tag in memory.tags:
            if tag.lower() in text:
                score += 1

        if score > 0:
            evidence.append(
                Evidence(
                    source="prior_history",
                    content=memory.content,
                    relevance=score
                )
            )

    return sorted(
        evidence,
        key=lambda item: item.relevance,
        reverse=True
    )


def validate_grounding(
    output,
    evidence
):
    errors = []

    if not evidence:
        errors.append(
            "No supporting evidence found."
        )

    if not output:
        errors.append(
            "Output is empty."
        )

    return errors


def create_grounded_output(
    email,
    memory_items
):
    evidence = retrieve_evidence(
        email,
        memory_items
    )

    if not evidence:
        return {
            "status": "rejected",
            "reason": "Output is not grounded.",
            "evidence": []
        }

    return {
        "status": "grounded",
        "sender": email.sender,
        "subject": email.subject,
        "evidence": [
            {
                "source": item.source,
                "content": item.content,
                "relevance": item.relevance
            }
            for item in evidence
        ]
    }