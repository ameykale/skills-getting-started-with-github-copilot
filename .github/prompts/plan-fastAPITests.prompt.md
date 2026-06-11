## Plan: Add FastAPI backend tests

TL;DR - Add pytest-based tests under `tests/` that exercise the FastAPI endpoints in `src/app.py` (GET activities, POST signup, DELETE participant). Use FastAPI's `TestClient` for synchronous tests and isolate/restore the in-memory `activities` state per test.

**Steps**
1. Create `tests/` directory and add `tests/test_app.py`.
2. In `tests/test_app.py`, provide a pytest fixture that:
   - Imports the `app` and `activities` objects from `src.app`.
   - Deep-copies the original `activities` before each test and restores it after the test to ensure isolation.
   - Creates a `TestClient(app)` instance for request calls.
3. Implement tests:
   - `test_get_activities`: call `GET /activities`, assert status 200 and response structure contains known activity keys.
   - `test_signup_success`: POST to `/activities/{activity_name}/signup?email=...`, assert 200 and that returned message includes the email; verify participant appears in `activities` (or via GET).
   - `test_signup_duplicate`: POST twice with the same email; assert second request returns 400 and appropriate error message.
   - `test_signup_invalid_activity`: POST to a non-existent activity, assert 404.
   - `test_remove_participant_success`: ensure DELETE `/activities/{activity_name}/participants?email=...` removes the participant and returns 200.
   - `test_remove_participant_not_registered`: DELETE a non-registered email, assert 404.
4. (Optional) Add `pytest` to `requirements.txt` or instruct contributors to install `pytest` in their environment.
5. Add a simple `README` note (or update `src/README.md`) with the test run command: `pytest -q`.

**Relevant files**
- `tests/test_app.py` — new tests file to implement (creates fixtures, implements the tests listed above).
- `src/app.py` — referenced for `app` and `activities` (tests import from here).
- `requirements.txt` (optional) — add `pytest` if desired.

**Verification**
1. Install test deps: `pip install -r requirements.txt` (or `pip install pytest` if not added).
2. Run tests: `pytest -q` should pass all tests.
3. Run individual tests for debugging: `pytest tests/test_app.py::test_signup_duplicate -q`.

**Decisions & assumptions**
- Tests use synchronous `TestClient` to keep test code simple and deterministic.
- Tests will isolate in-memory `activities` by copying and restoring to avoid cross-test leakage.
- **Tests follow AAA (Arrange-Act-Assert) pattern:**
  - **Arrange:** Set up test data, fixtures, and preconditions.
  - **Act:** Execute the code/endpoint being tested.
  - **Assert:** Verify the results against expected outcomes.
- No changes to production code are required; tests interact with existing endpoints.

**Further considerations**
1. If you prefer async tests using `httpx.AsyncClient` and `pytest-asyncio`, we can update the plan to include `pytest-asyncio` and asynchronous test patterns.
2. Consider adding a CI job (GitHub Actions) to run tests on push/PR — I can draft the workflow if you want.
