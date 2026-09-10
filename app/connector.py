from tools import read_inbox, lookup_contact


class EmailConnector:
    """
    Typed interface between the agent and external data sources.
    """

    def get_inbox(self):
        return read_inbox()

    def get_contact(self, email_address: str):
        return lookup_contact(email_address)

    def get_tasks(self):
        # Temporary implementation.
        # Calendar/task integration comes later.
        return []


class MockEmailConnector(EmailConnector):
    """
    Alternative data source used to prove
    that the agent does not depend on one source.
    """

    def get_inbox(self):
        return [
            {
                "sender": "newstudent@gmail.com",
                "subject": "Assignment extension",
                "body": "Can I get one more day?"
            }
        ]

    def get_contact(self, email_address: str):
        return {
            "name": "New Student",
            "category": "Student"
        }

    def get_tasks(self):
        return [
            "Review assignment extension request"
        ]