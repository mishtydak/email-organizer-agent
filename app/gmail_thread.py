from dataclasses import dataclass


@dataclass
class ThreadMessage:
    message_id: str
    thread_id: str
    sender: str
    subject: str
    body: str


def get_header(
    headers,
    name
):
    for header in headers:

        if header["name"].lower() == name.lower():
            return header["value"]

    return ""


def extract_body(payload):

    if not payload:
        return ""

    mime_type = payload.get(
        "mimeType",
        ""
    )

    body_data = (
        payload
        .get("body", {})
        .get("data")
    )

    if body_data:

        import base64

        decoded = base64.urlsafe_b64decode(
            body_data + "=="
        )

        return decoded.decode(
            "utf-8",
            errors="ignore"
        )

    parts = payload.get(
        "parts",
        []
    )

    collected = []

    for part in parts:

        part_body = extract_body(
            part
        )

        if part_body:
            collected.append(
                part_body
            )

    return "\n".join(
        collected
    )


def parse_thread_messages(
    messages
):

    result = []

    for message in messages:

        payload = message.get(
            "payload",
            {}
        )

        headers = payload.get(
            "headers",
            []
        )

        sender = get_header(
            headers,
            "From"
        )

        subject = get_header(
            headers,
            "Subject"
        )

        body = extract_body(
            payload
        )

        # Gmail can return an empty decoded body
        # for some messages, so retain the snippet.
        if not body:
            body = message.get(
                "snippet",
                ""
            )

        result.append(
            ThreadMessage(
                message_id=message.get(
                    "id",
                    ""
                ),
                thread_id=message.get(
                    "threadId",
                    ""
                ),
                sender=sender,
                subject=subject,
                body=body
            )
        )

    return result