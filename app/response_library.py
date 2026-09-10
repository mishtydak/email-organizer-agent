STANDARD_RESPONSES = [
    {
        "title": "Project Extension",
        "keywords": ["extension", "deadline", "project"],
        "response": (
            "Dear Student,\n\n"
            "Your extension request has been noted. "
            "Please submit the revised project by the agreed deadline.\n\n"
            "Regards,\nFaculty"
        )
    },
    {
        "title": "Meeting Request",
        "keywords": ["meeting", "schedule", "discuss"],
        "response": (
            "Dear Colleague,\n\n"
            "Thank you for reaching out. "
            "I will review my schedule and confirm a suitable meeting time.\n\n"
            "Regards,\nFaculty"
        )
    },
    {
        "title": "Submission Deadline",
        "keywords": ["submission", "submit", "deadline", "report"],
        "response": (
            "Dear Student,\n\n"
            "Please ensure that the required submission is completed "
            "before the specified deadline.\n\n"
            "Regards,\nFaculty"
        )
    }
]


def find_standard_response(subject: str, body: str):
    text = f"{subject} {body}".lower()

    best_match = None
    best_score = 0

    for item in STANDARD_RESPONSES:
        score = sum(
            1 for keyword in item["keywords"]
            if keyword.lower() in text
        )

        if score > best_score:
            best_score = score
            best_match = item

    return best_match