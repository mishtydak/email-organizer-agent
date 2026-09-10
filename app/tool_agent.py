from tools import read_inbox, lookup_contact


def find_email_context(sender: str):
    """
    Tool-using agent.

    It first retrieves the inbox using the inbox tool,
    then uses the contact lookup tool for the matching email.
    """

    # Tool 1: get the actual emails
    emails = read_inbox()

    # Find the requested email
    matching_email = None

    for email in emails:
        if email.sender == sender:
            matching_email = email
            break

    if matching_email is None:
        return None

    # Tool 2: get contact information
    contact = lookup_contact(sender)

    return {
        "email": matching_email,
        "contact": contact
    }