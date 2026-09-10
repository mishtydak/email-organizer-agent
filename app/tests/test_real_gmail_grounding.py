import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)




from gmail_connector import (
    GmailConnector
)

from gmail_grounding import (
    GmailThreadGrounder
)


def main():

    print(
        "\n======================================"
    )

    print(
        "REAL GMAIL THREAD GROUNDING TEST"
    )

    print(
        "======================================\n"
    )

    gmail = GmailConnector()

    emails = gmail.fetch_emails(
        max_results=20
    )

    if not emails:

        print(
            "No Gmail messages found."
        )

        return

    print(
        f"Found {len(emails)} emails.\n"
    )

    for index, email in enumerate(
        emails,
        start=1
    ):

        print(
            f"{index}. {email.subject}"
        )

        print(
            f"   Sender: {email.sender}"
        )

        print(
            f"   Thread ID: {email.thread_id}"
        )

    # Pick the first real message.
    selected_email = None

    for email in emails:

     if not email.thread_id:
        continue

     messages = gmail.get_thread_messages(
        email.thread_id
     )

     if len(messages) >= 2:
        selected_email = email
        break


    if selected_email is None:
     print(
        "\nNo multi-message Gmail thread "
        "was found in the first 20 emails."
     )
     print(
        "The Gmail API connection is working, "
        "but your recent inbox does not contain "
        "a conversation with multiple messages."
     )
     return


    email = selected_email

    print(
        "\n========== SELECTED EMAIL =========="
    )

    print(
        "Subject:",
        email.subject
    )

    print(
        "Thread:",
        email.thread_id
    )

    grounder = GmailThreadGrounder(
        gmail
    )

    result = grounder.ground_email(
        email
    )

    print(
        "\n========== GROUNDING RESULT =========="
    )

    print(
        "Status:",
        result["status"]
    )

    if result["status"] == "grounded":

        print(
            "\nEvidence:"
        )

        for evidence in result[
            "evidence"
        ]:

            print(
                "\n------------------------------"
            )

            print(
                "Sender:",
                evidence["sender"]
            )

            print(
                "Subject:",
                evidence["subject"]
            )

            print(
                "Relevance:",
                evidence["relevance"]
            )

            print(
                "Content:"
            )

            print(
                evidence["content"][:1000]
            )

        assert len(
            result["evidence"]
        ) > 0

        print(
            "\nPASS: REAL GMAIL THREAD "
            "GROUNDING WORKS."
        )

    else:

        print(
            "\nNo relevant prior message "
            "was found in this thread."
        )

        print(
            "This is a valid rejection, "
            "not an API failure."
        )


if __name__ == "__main__":
    main()