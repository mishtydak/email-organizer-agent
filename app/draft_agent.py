from response_library import find_standard_response


def draft_reply(email):
    match = find_standard_response(
        email.subject,
        email.body
    )

    if match is None:
        return {
            "status": "no_template",
            "subject": f"Re: {email.subject}",
            "body": None
        }

    return {
        "status": "draft",
        "template": match["title"],
        "subject": f"Re: {email.subject}",
        "body": match["response"]
    }