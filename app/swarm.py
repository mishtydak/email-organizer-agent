def fan_out(emails: list) -> list:
    return [[email] for email in emails]

def process_email(email):
    
    return {
        

        "sender": email.sender,
        "subject": email.subject,
        "status": "processed"
    }
    
def fan_in(results: list) -> list:
    merged_results = []

    for result in results:
        merged_results.append(result)

    return merged_results

from concurrent.futures import ThreadPoolExecutor


def run_parallel(emails: list) -> list:
    with ThreadPoolExecutor() as executor:
        results = list(
            executor.map(process_email, emails)
        )

    return results

"""def run_sequential(emails: list) -> list:
    results = []

    for email in emails:
        results.append(process_email(email))

    return results

def measure_execution(emails: list):
    start = time.perf_counter()
    run_sequential(emails)
    sequential_time = time.perf_counter() - start

    start = time.perf_counter()
    run_parallel(emails)
    parallel_time = time.perf_counter() - start

    print(f"Sequential time: {sequential_time:.2f} seconds")
    print(f"Parallel time:   {parallel_time:.2f} seconds")"""
    
if __name__ == "__main__":
    from tools import read_inbox

    emails = read_inbox()
    