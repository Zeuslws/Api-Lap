# API lab results

Observed on 9 November 2026 (Asia/Bangkok). These answers distinguish live
observations from expected behavior. See the saved curl evidence and test report.

## Part 0

- Step 0.1: **18** pizza names.
- Step 0.3: Without a token, `/api/tools` returned **401** and
  `{"error":"authentication failed"}`.
- Step 0.4: The vegetarian recommendation was **The Hurt Napoletana**.
  Pizza names vary because recommendations are random.
- Step 0.12: Optional no-session experiment **not performed**. No three-run
  outcome is claimed.
- Step 0.16: For the three distinct supported tools, the blocks are **0, 1, 2,
  and 3 tools excluded**. Inputs are `[]`, `["Knife"]` (also `["Scissors"]`),
  `["Knife", "Scissors"]`, and `["Knife", "Pizza cutter", "Scissors"]`.
  The original two cases both covered only the one-excluded block.

## Defect report: Defect 1

- **Title:** Excluding every tool causes an internal server error.
- **Request:** `POST https://quickpizza.grafana.com/api/pizza`, with a valid
  login token, `Content-Type: application/json`, and body
  `{"excludedTools":["Knife","Pizza cutter","Scissors"]}`.
- **Expected result:** HTTP **400**, with a nonempty JSON error message
  explaining that the restriction cannot be satisfied. This is the product
  owner requirement stated in the lab.
- **Actual result:** HTTP **500**, with an **empty response body**. Confirmed
  independently using curl and by the pytest case.
- **Severity:** **Medium**: an ordinary customer restriction produces a server
  error and gives clients no useful explanation. No server-wide outage or data
  loss was observed.
- **Tracking:** `test_excluding_all_tools_is_bad_request` asserts the desired
  behavior and uses `xfail(strict=True)`. It does not assert that 500 is correct.

## Part A

Step A4 observed status codes:

| Other user's operation | Observed status | Owner's rating after attempt |
| --- | --- | --- |
| Read (GET) | **404** | Unchanged |
| Change (PUT) | **400** | Unchanged |
| Delete (DELETE) | **400** | Unchanged |

The nine creation cases cover the selected base-choice model. Update boundary
cases check both the immediate response and persisted data; rejected updates
leave the original rating unchanged. Every ownership test also reads the
rating as its owner to verify that it is still intact.

## Part B

### 1. Integration tests and unit tests

A real API test can reveal routing/authentication middleware errors, such as
an invalid token being accepted before a handler runs. It can also reveal
persistence and deployment integration problems, such as a successful write
that is not returned by a later read, or a login reaching a different backend.
Stubbed unit tests cannot verify those real components working together.
Unit tests are still useful because they are fast and deterministic and can
exercise rare error paths without network availability or shared server state.

### 2. Fresh users and data ownership

Fresh unique usernames prevent duplicate-name collisions and give each test
its own ratings. The public token refers to shared data that other people can
change, so using it for rating writes would both disrupt others and make tests
unreliable. For Project 2, create identifiable test-owned customers, orders or
bookings using unique names, save their IDs, and clean up only those records.
Use the group's authorized credentials rather than anyone else's data.

### 3. Why one session is necessary

The demo service uses multiple backend servers with server-local user state.
The session keeps the AWSALB load-balancer cookie so registration, login and
later requests can reach the same backend. Without cookies, login may reach a
server that does not know the newly created user. This makes results flaky
without a code change. The curl response included AWSALB/AWSALBCORS cookies;
the optional three no-session runs were not performed.

### 4. The excluded-tools defect and xfail

The **three excluded tools** block revealed the defect: no cutting tool remains.
A 400 JSON response tells the caller to change its restrictions and provides an
error it can display. A 500 empty body looks like an unexpected server failure;
a client that assumes JSON may also raise a decoding error, and it cannot
explain which input to fix. Keeping the test as strict xfail preserves the
expected contract and regression evidence. Once it passes, strict mode makes
the suite fail with XPASS, prompting removal of the marker.

### 5. Coverage counts

The characteristic block counts are 3, 4, 2 and 3. Base choice uses one all-base
case plus one case for every non-base block:
`1 + (3 - 1) + (4 - 1) + (2 - 1) + (3 - 1) = 9`.
The nominal Cartesian product is `3 * 4 * 2 * 3 = 72` combinations.
The supplied model has a feasibility limitation: numeric-value blocks cannot
literally apply to missing or arbitrary text stars. Thus 72 is the model's
nominal all-combinations count, not a claim that every combination is executable.

### 6. Accessing another user's rating

Observed: **GET 404, PUT 400, DELETE 400**. For an authenticated non-owner,
I would normally expect 403 Forbidden, or a consistent 404 to conceal whether
the resource exists. 401 is more appropriate for missing or invalid credentials.
The 400 responses are less precise and inconsistent with GET, but all attempts
were refused and the owner could still read the unchanged rating. Thus these
results do not demonstrate an access-control bypass. They satisfy the lab's
explicit 4xx acceptance criterion; calling the status-code inconsistency a
contract defect would require a more specific API specification.

### 7. A made-up token

The read-only request with `Authorization: token 0000000000000000` returned
**200** with a JSON object containing `ratings`; the observed list contained
**50 ratings**. No ratings were created, changed or deleted using this token.
The saved evidence contains only the response keys and count, not the returned
rating records.

Under the lab's requirement that access requires a logged-in user's token,
this is an **authentication defect**: an invented token should receive 401.
On a real system, accepting such a token could let a stranger read records
without signing in. Whether the same defect permits writes or exposes other
users' private data would require separate authorized investigation; this
read-only observation does not prove those additional capabilities. A demo
may intentionally expose sample data, but that would need an explicit
exception to the stated authentication contract.

### 8. API tests versus browser tests

API tests can directly send malformed JSON values or missing headers and check
precise status codes and error bodies, including inputs a form might prevent.
Browser tests can check visible layout, button behavior and whether an error is
actually displayed to the user; an API response alone cannot prove those things.

## Execution and submission notes

Final complete run: **32 passed, 1 xfailed, no failures or teardown errors**.
The delete test also passed independently (**1 passed**). The first full run
revealed that deleting an already-deleted rating returns 400 during cleanup;
cleanup now lists this test user's remaining ratings and deletes each once.
The final HTML report comes from the complete rerun after that fix.

The lab is individual homework. Review these draft reflection answers and make
sure you can explain the tests before submitting. The source, README, results
and HTML report are prepared locally; GitHub publishing and MyCourses
submission have not been performed. Historical intermediate runs from every
guided step are not claimed; this package implements and verifies the final
suite. The optional Step 0.12 experiment was omitted.
