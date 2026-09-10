from graph import run_graph
from governance import GovernedOutput, request_approval
from specialists import (
    AcademicEmailSpecialist,
    validate_specialist_result
)


def run_capstone():
    print("\n========== EMAIL ORGANIZER AGENT ==========\n")

    # 1. Run the triage pipeline
    state = run_graph()

    if not state.validation_passed:
        print("Pipeline failed validation.")
        return

    # 2. Apply the domain specialist
    specialist = AcademicEmailSpecialist()

    for email in state.emails:
        result = specialist.analyze(email)

        errors = validate_specialist_result(result)

        if errors:
            print("Specialist validation failed:")
            for error in errors:
                print("-", error)
            return

        print(f"\nSpecialist result for: {email.subject}")
        print(result)

    # 3. Create governed draft
    output = GovernedOutput(
        content={
            "triage": state.triage_draft
        }
    )

    print("\n========== TRIAGE DRAFT ==========")
    for draft in state.triage_draft:
        print(draft)

    # 4. Human approval gate
    output = request_approval(output)

    print("\nFinal governance state:", output.state.value)


if __name__ == "__main__":
    run_capstone()