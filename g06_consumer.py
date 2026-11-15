import requests

BASE_URL = "http://127.0.0.1:5000"
results = []


def send_request(method, endpoint, description, expected_status, data=None):
    try:
        response = requests.request(
            method,
            BASE_URL + endpoint,
            json=data,
            timeout=10
        )

        actual_status = response.status_code
        passed = actual_status == expected_status

        print(f"\n{description}")
        print(f"Request: {method} {endpoint}")
        print(f"Status Code: {actual_status}")

        try:
            print("Response:", response.json())
        except ValueError:
            print("Response:", response.text)

        results.append({
            "method": method,
            "endpoint": endpoint,
            "expected": expected_status,
            "actual": actual_status,
            "passed": passed
        })

        return response

    except requests.exceptions.RequestException as error:
        print(f"\nRequest failed: {error}")

        results.append({
            "method": method,
            "endpoint": endpoint,
            "expected": expected_status,
            "actual": "ERROR",
            "passed": False
        })

        return None


def find_unused_book_id():
    response = requests.get(BASE_URL + "/books", timeout=10)
    response.raise_for_status()

    books = response.json()
    existing_ids = {book["id"] for book in books}

    test_id = 143

    while test_id in existing_ids:
        test_id += 1

    return test_id


def print_summary():
    print("\n" + "=" * 25)
    print("SUMMARY REPORT")
    print("=" * 25)

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"

        print(
            f"{status} | {result['method']} {result['endpoint']} "
            f"| Expected: {result['expected']} "
            f"| Actual: {result['actual']}"
        )

    passed_count = sum(result["passed"] for result in results)
    failed_count = len(results) - passed_count

    print("-" * 25)
    print(f"Total Requests: {len(results)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print("=" * 25)


print("=" * 25)
print("GROUP 6 - LIBRARY BOOK BORROWING API CONSUMER")
print("GROUP 2 - PARTNER API INTEGRATION")
print("=" * 25)

try:
    test_id = find_unused_book_id()
    invalid_id = 999999

    send_request(
        "GET", "/books",
        "Retrieve all books", 200
    )

    send_request(
        "GET", "/books/1",
        "Retrieve an existing book", 200
    )

    send_request(
        "GET", f"/books/{invalid_id}",
        "Retrieve a nonexistent book", 404
    )

    created = send_request(
        "POST", f"/books/{test_id}/add",
        "Add a new book", 201,
        {
            "title": "Consumer Test Book",
            "author": "CheckInSync Group"
        }
    )

    if created is not None and created.status_code == 201:

        send_request(
            "POST", f"/books/{test_id}/add",
            "Add a duplicate book ID", 409,
            {
                "title": "Duplicate Test Book",
                "author": "CheckInSync Group"
            }
        )

        send_request(
            "POST", f"/books/{test_id + 1}/add",
            "Add a book with missing author", 400,
            {
                "title": "Incomplete Test Book"
            }
        )

        send_request(
            "PUT", f"/books/{test_id}/borrow",
            "Borrow an available book", 200
        )

        send_request(
            "PUT", f"/books/{test_id}/return",
            "Return a borrowed book", 200
        )

        send_request(
            "PUT", f"/books/{test_id}/reserve",
            "Update using an invalid action", 400
        )

        send_request(
            "PUT", f"/books/{invalid_id}/borrow",
            "Borrow a nonexistent book", 404
        )

        deleted = send_request(
            "DELETE", f"/books/{test_id}/delete",
            "Delete an existing book", 200
        )

        if deleted is not None and deleted.status_code == 200:
            send_request(
                "DELETE", f"/books/{test_id}/delete",
                "Delete an already deleted book", 404
            )

    else:
        print("\nBook creation failed. Dependent tests skipped.")

except requests.exceptions.RequestException as error:
    print("\nUnable to prepare API tests:", error)

print_summary()
