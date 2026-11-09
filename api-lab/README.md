# QuickPizza API lab

ITCS386: Software Verification and Validation, Week 11. Tests use the real
QuickPizza API at https://quickpizza.grafana.com. Run serially, only as needed;
this is a shared demonstration service.

## Install and run

Use Python 3.10 or newer. From this folder on macOS/Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -v --html=report.html --self-contained-html
```

On Windows PowerShell, create the environment with `python -m venv .venv`,
activate it with `.venv\Scripts\Activate.ps1`, then run the same pip and pytest
commands. Open `report.html` in a browser after the run.

Expected current result: **32 passed, 1 xfailed**. The strict expected failure
tracks the confirmed all-tools-excluded defect. If the service fixes it, pytest
reports XPASS as a failure so the marker can be removed. Failures in networking
or user setup must be investigated; they are not evidence of this defect.

Dependency versions are pinned to those used for the report. The initial
pytest 9.2.0 installation crashed internally during collection in this Python
3.10 environment; pytest 9.1.1 collected the suite successfully.

To verify a CRUD test independently:

```sh
pytest -v test_ratings.py::test_delete_rating
```

## Input domain model: POST /api/ratings

The base choice is integer `3`, a newly generated existing pizza, and the user's
own login token. Each non-base case changes one characteristic. These are the
lab's selected blocks; this is not an exhaustive JSON type/security model.
For text and missing stars, numeric-range classification is not applicable;
the valid numeric base is replaced by the selected type/presence case.

| Characteristic | Block | Representative | Test in test_create_rating.py |
| --- | --- | --- | --- |
| C1: value of stars | Below 1 | `0` | `test_stars_out_of_range[0]` |
| C1: value of stars | 1 to 5 (base) | `3` | `test_base_choice_is_saved` |
| C1: value of stars | Above 5 | `6` | `test_stars_out_of_range[6]` |
| C2: type of stars | Whole number (base) | `3` | `test_base_choice_is_saved` |
| C2: type of stars | Decimal | `3.5` | `test_invalid_star_type[decimal]` |
| C2: type of stars | Text | `"3"` | `test_invalid_star_type[text]` |
| C2: type of stars | Missing | Omit field | `test_missing_stars` |
| C3: pizza | Exists (base) | Fresh pizza ID | `test_base_choice_is_saved` |
| C3: pizza | Does not exist | `999999999` | `test_nonexistent_pizza` |
| C4: token | User's own (base) | Login token | `test_base_choice_is_saved` |
| C4: token | None | No header | `test_invalid_token[none]` |
| C4: token | Wrong length | `token short` | `test_invalid_token[short]` |

Base choice: `1 + (3-1) + (4-1) + (2-1) + (3-1) = 9` cases.
The model's nominal all-combinations count is `3 * 4 * 2 * 3 = 72`;
some value/type combinations are infeasible, as explained above.

PUT boundaries are `0, 1, 5, 6`. Each update is followed by a GET; rejected
updates must leave the whole rating unchanged. Ownership tests use two fresh
users and check the owner's saved rating after each other-user request.

## Isolation and cleanup

A session-scoped `requests.Session` keeps load-balancer cookies. Each test that
needs authenticated data gets a unique `lab-` username and its own login token.
All requests have a 30-second timeout. Tests never mutate public-token ratings.
The auth fixture removes all remaining ratings belonging to that test user,
including fixture-created ratings and unexpected successful creates. It lists
ratings before deleting, so a rating already deleted by its test is not deleted
a second time. The lab supplies no user/pizza deletion workflow, so those temporary
users and generated pizzas remain on the demo service.

The public token in `auth.txt` is the documented practice token. `madeup.txt`
is only for the read-only Part B observation; never use it to write data.
Actual login tokens and cookie jars are not saved in the repository. Short
pytest tracebacks avoid displaying authentication fixture values in reports.

## Curl examples and evidence

```sh
curl -i https://quickpizza.grafana.com/api/names
curl -i https://quickpizza.grafana.com/api/tools
curl -i -H "@auth.txt" -H "Content-Type: application/json" -d "@veg.json" https://quickpizza.grafana.com/api/pizza
curl -i -H "@auth.txt" -H "Content-Type: application/json" -d "@excluded_all.json" https://quickpizza.grafana.com/api/pizza
curl -i -H "@madeup.txt" https://quickpizza.grafana.com/api/ratings
```

In Windows PowerShell use `curl.exe`. Part A errors were first observed through
curl with a temporary cookie jar, a newly registered user, and its login token.
`evidence/curl-observations.json` records those requests and responses with login
tokens redacted and the made-up-token response reduced to keys and count.
The saved `decimal.json`, `text.json`, `missing.json`, and `nonexistent.json`
are the observed curl inputs. Their pizza IDs are historical; replace existing
pizza IDs with a newly generated pizza from your own session before reuse.
`RESULTS.md` contains the observations and reflection answers. `report.html`
is the full test report; `evidence/pytest-output.txt` and `evidence/results.xml`
retain the console output and exact ownership status properties.

## Submission

Review the code and reflection answers. Create a public GitHub repository named
`api-lab`, upload this folder's contents (excluding `.venv` and caches), and
submit the repository URL on MyCourses. No GitHub upload or MyCourses
submission has been performed by this local preparation.
