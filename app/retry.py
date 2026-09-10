def run_with_retries(action, max_retries=2):
    attempts = 0

    while attempts <= max_retries:
        try:
            return action()
        except Exception as error:
            attempts += 1

            print(f"Attempt failed: {error}")

            if attempts > max_retries:
                raise RuntimeError(
                    "Maximum retry limit exceeded."
                )

            print(f"Retrying... ({attempts}/{max_retries})")
            
def retry_operation(operation, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return operation()

        except Exception as error:
            diagnosis = diagnose_error(error)

            print(
                f"Operation failed "
                f"(attempt {attempt + 1}/{max_retries + 1})"
            )
            print(f"Diagnosis: {diagnosis}")

            if attempt == max_retries:
                print("Giving up on this operation.")
                return None


def diagnose_error(error: Exception) -> str:
    if isinstance(error, ValueError):
        return "Invalid data"

    if isinstance(error, KeyError):
        return "Missing required field"

    if isinstance(error, TypeError):
        return "Invalid data type"

    return "Unknown failure"


def retry_with_diagnosis(operation, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return operation()

        except Exception as error:
            diagnosis = diagnose_error(error)

            print(
                f"\nFailure detected: {error}"
            )
            print(
                f"Diagnosis: {diagnosis}"
            )

            if attempt == max_retries:
                print("Retry budget exhausted.")
                return None

            print(
                f"Regenerating failing operation "
                f"({attempt + 1}/{max_retries})..."
            )
            
            
def test_recovery():
    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise ValueError("invalid priority")

        return "Recovered"

    return retry_with_diagnosis(
        operation,
        max_retries=2
    )