from dataclasses import dataclass


@dataclass
class AcademicEmailResult:
    category: str
    requires_action: bool
    reason: str


class AcademicEmailSpecialist:
    def analyze(self, email) -> AcademicEmailResult:

        subject = email.subject.lower()
        body = email.body.lower()

        if "extension" in subject or "extension" in body:
            return AcademicEmailResult(
                category="Academic Request",
                requires_action=True,
                reason="Student is requesting an academic deadline extension."
            )

        if "meeting" in subject or "meeting" in body:
            return AcademicEmailResult(
                category="Academic Meeting",
                requires_action=True,
                reason="Email contains a meeting-related request."
            )

        return AcademicEmailResult(
            category="Academic Information",
            requires_action=False,
            reason="No explicit academic action was identified."
        )
        
        
def validate_specialist_result(result: AcademicEmailResult) -> list[str]:
    errors = []

    if not result.category:
        errors.append("Missing category")

    if not isinstance(result.requires_action, bool):
        errors.append("requires_action must be boolean")

    if not result.reason:
        errors.append("Missing reason")

    return errors


class SpecialistRegistry:
    def __init__(self):
        self.specialists = {}

    def register(self, name: str, specialist):
        self.specialists[name] = specialist

    def get(self, name: str):
        return self.specialists.get(name)