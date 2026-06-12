# Password Generator Version 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan with the three specialized agents defined below. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a secure Python command-line password generator with selectable character sets, configurable length, and optional clipboard copying.

**Architecture:** Keep password generation in an importable module so its behavior can be tested independently from command-line parsing. Use a thin `pw-gen.py` entry point, Python's `secrets` module for secure randomness, `argparse` for the CLI, and `pyperclip` only when clipboard copying is requested.

**Tech Stack:** Python 3.11+, uv, Ruff, pytest, pyperclip

---

## Required Multi-Agent Workflow

Implementation must use three separate agents with distinct responsibilities:

1. **Senior Test Engineer**
   - Translates each requirement in this plan into focused pytest coverage.
   - Writes tests before the corresponding implementation.
   - Runs the new tests and records the expected failure before handing off.
   - Uses Ruff to format and lint all test code before committing it.
   - Does not write production implementation code.

2. **Senior Python Engineer**
   - Implements the minimum Python code needed to satisfy the approved tests and this plan.
   - Uses Ruff to format and lint all Python code before committing it.
   - Runs focused pytest tests after each change and the complete pytest suite before publishing.
   - Owns project metadata, CLI code, password generation, clipboard integration, and documentation.
   - Does not weaken, delete, or rewrite a failing test without approval from the Senior Test Engineer.

3. **Senior Code Reviewer**
   - Reviews the tests and implementation after they are committed, pushed, and presented in a GitHub pull request.
   - Compares the PR against every interface, behavior, task, and assumption in this plan.
   - Runs Ruff formatting and lint checks, the complete pytest suite, and documented CLI acceptance checks independently.
   - Reports findings with file and line references and blocks approval for missing requirements, security defects, regressions, or inadequate tests.
   - Records a review verdict only when the implementation and tests fully match this plan and all verification passes; an independent human supplies formal PR approval when repository policy requires it.

For each feature task, use this handoff sequence:

1. The Senior Test Engineer writes and runs failing tests.
2. The Senior Python Engineer implements the behavior and makes the tests pass.
3. Each engineer runs Ruff over their changes before committing to the same feature branch.
4. Agent handoffs are sequential in the shared worktree: only the active agent may edit, run mutating tools, or commit, and it must finish or hand off before the next agent starts.
5. After all tasks are complete, the branch is pushed and a GitHub pull request is opened.
6. The Senior Code Reviewer reviews and verifies the PR. Any findings return to the responsible Test or Python Engineer for correction, followed by another review cycle.

## Required Quality Commands

- Use Ruff as the only formatter and linter:

```bash
uv run ruff format .
uv run ruff check --fix .
```

- Before every implementation commit and every push, verify formatting, linting, and tests:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

- Ruff must pass without warnings or errors, and pytest must report a fully passing suite.
- The only exception is an intentional test-first commit by the Senior Test Engineer: Ruff must still pass, while the focused pytest command must fail for the expected missing behavior. Do not push that red commit until the Senior Python Engineer has added the corresponding implementation and the full suite passes.
- Do not substitute Black, Flake8, isort, unittest, or another formatter, linter, or test runner.

## File Structure

- Create `password_generator.py` for character-set selection, secure generation, argument parsing, clipboard handling, and the testable `main()` function.
- Create `pw-gen.py` as the executable entry point that calls `password_generator.main()`.
- Create `tests/test_password_generator.py` for generation, validation, CLI, and clipboard tests.
- Create `pyproject.toml` for Python metadata, the `pyperclip` runtime dependency, and Ruff and pytest development dependencies.
- Modify `README.md` with installation, defaults, flags, usage examples, and validation behavior.

## Public Interfaces and Behavior

```python
def generate_password(
    length: int = 8,
    include_lowercase: bool = True,
    include_uppercase: bool = False,
    include_digits: bool = False,
    include_special: bool = False,
) -> str:
    ...


def build_parser() -> argparse.ArgumentParser:
    ...


def main(argv: list[str] | None = None) -> int:
    ...
```

- `python3 pw-gen.py` and `uv run pw-gen.py` generate an 8-character lowercase password.
- `uv run pw-gen.py` resolves project dependencies automatically. Direct `python3 pw-gen.py` usage requires the uv environment to be activated first when `--cb` is used.
- `-l LENGTH` sets the password length and defaults to `8`.
- `-c`, `-u`, `-d`, and `-s` select lowercase, uppercase, digits, and special characters respectively.
- When no character-set flags are supplied, lowercase is selected automatically.
- Once any character-set flag is supplied, only the explicitly selected sets are used.
- Every selected character set must appear at least once in the result.
- Special characters are the characters in `string.punctuation`.
- Password generation uses `secrets.choice`; the final password is shuffled with a cryptographically secure Fisher-Yates shuffle driven by `secrets.randbelow`.
- A length below `1` is invalid.
- A length smaller than the number of selected character sets is invalid because representation of every selected set cannot be guaranteed.
- Calling `generate_password()` with all four `include_*` arguments set to `False` raises `ValueError("at least one character set must be selected")`.
- Successful generation prints only the password followed by a newline.
- `--cb` copies the same generated password to the clipboard with `pyperclip.copy()` and still prints it.
- `pyperclip` is imported lazily inside the `--cb` execution path so generation without clipboard copying does not load or require the clipboard integration.
- Argument and length errors use argparse-style stderr output and exit code `2`.
- Clipboard failures print a concise `error: unable to copy password to clipboard: ...` message to stderr and return exit code `1`.

## Task 1: Establish Project Metadata

**Owner:** Senior Python Engineer

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Create the uv-compatible project configuration**

Define:

```toml
[project]
name = "password-generator"
version = "0.1.0"
description = "A secure command-line password generator"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pyperclip>=1.9,<2",
]

[dependency-groups]
dev = [
    "pytest>=8,<10",
    "ruff>=0.11,<1",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"

[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

- [ ] **Step 2: Verify uv can resolve the configuration**

Run:

```bash
uv sync --dev
```

Expected: Ruff, pytest, and pyperclip resolve successfully and a lockfile is created.

- [ ] **Step 3: Commit the metadata**

```bash
git add pyproject.toml uv.lock
git commit -m "build: configure password generator project"
```

## Task 2: Implement Secure Password Generation

**Test owner:** Senior Test Engineer

**Implementation owner:** Senior Python Engineer

**Files:**
- Create: `password_generator.py`
- Create: `tests/test_password_generator.py`

- [ ] **Step 1: Write failing tests for the default behavior**

Add tests asserting that `generate_password()` returns exactly eight characters and that every character belongs to `string.ascii_lowercase`.

- [ ] **Step 2: Run the default-generation tests**

Run:

```bash
uv run pytest tests/test_password_generator.py -k default
```

Expected: FAIL because `password_generator` does not exist.

- [ ] **Step 3: Implement the default generator**

Create `generate_password()` with the public signature above. Build the enabled-set list from the Boolean parameters and draw characters with `secrets.choice`. The function's default arguments enable lowercase; if callers explicitly disable every set, validation rejects the request.

- [ ] **Step 4: Verify the default behavior**

Run:

```bash
uv run pytest tests/test_password_generator.py -k default
```

Expected: PASS.

- [ ] **Step 5: Write failing tests for selected character sets**

Add parameterized tests covering lowercase, uppercase, digits, and punctuation individually. Add a combined test that requests all four sets and asserts:

```python
assert any(character in string.ascii_lowercase for character in password)
assert any(character in string.ascii_uppercase for character in password)
assert any(character in string.digits for character in password)
assert any(character in string.punctuation for character in password)
```

Also assert that characters never come from unselected sets.

- [ ] **Step 6: Implement guaranteed set representation**

Choose one character from each enabled set, fill remaining positions from the combined pool, then apply an in-place Fisher-Yates shuffle:

```python
for index in range(len(characters) - 1, 0, -1):
    swap_index = secrets.randbelow(index + 1)
    characters[index], characters[swap_index] = (
        characters[swap_index],
        characters[index],
    )
```

- [ ] **Step 7: Verify character-set behavior**

Run:

```bash
uv run pytest tests/test_password_generator.py -k "character or selected"
```

Expected: PASS.

- [ ] **Step 8: Write failing validation tests**

Add tests asserting `generate_password()` raises `ValueError` when:

- `length` is zero or negative.
- `length` is smaller than the number of enabled character sets.
- All four `include_*` arguments are explicitly `False`.

Add boundary tests asserting:

- Length `1` succeeds when exactly one character set is enabled.
- Length equal to the number of enabled character sets succeeds and contains one character from every selected set.

- [ ] **Step 9: Implement validation**

Raise:

```python
ValueError("password length must be at least 1")
```

or:

```python
ValueError(
    "password length must be at least the number of selected character sets"
)
```

or:

```python
ValueError("at least one character set must be selected")
```

as appropriate. The generator function treats all-false arguments as invalid; the CLI is responsible for applying the lowercase default when the user supplies no character-set flags.

- [ ] **Step 10: Run the generation test suite**

Run:

```bash
uv run ruff format .
uv run ruff check --fix .
uv run ruff format --check .
uv run ruff check .
uv run pytest tests/test_password_generator.py
```

Expected: Ruff reports no formatting or lint issues, and all generation and validation pytest tests pass.

- [ ] **Step 11: Commit secure generation**

```bash
git add password_generator.py tests/test_password_generator.py
git commit -m "feat: add secure password generation"
```

## Task 3: Add the Command-Line Interface

**Test owner:** Senior Test Engineer

**Implementation owner:** Senior Python Engineer

**Files:**
- Modify: `password_generator.py`
- Modify: `tests/test_password_generator.py`
- Create: `pw-gen.py`

- [ ] **Step 1: Write failing parser tests**

Test `build_parser().parse_args()` for:

- Default length `8`.
- `-l 12`.
- Each character flag.
- All character flags together.
- `--cb`.
- Automatic `--help` output and successful exit.

- [ ] **Step 2: Run the parser tests**

Run:

```bash
uv run pytest tests/test_password_generator.py -k parser
```

Expected: FAIL because `build_parser()` is not implemented.

- [ ] **Step 3: Implement `build_parser()`**

Use `argparse.ArgumentParser` with:

```text
-l LENGTH   Password length (default: 8)
-c          Include lowercase letters
-u          Include uppercase letters
-d          Include digits
-s          Include special characters
--cb        Copy the generated password to the clipboard
```

Let argparse provide `-h` and `--help`.

- [ ] **Step 4: Verify parser behavior**

Run:

```bash
uv run pytest tests/test_password_generator.py -k parser
```

Expected: PASS.

- [ ] **Step 5: Write failing `main()` tests**

Use `capsys` and monkeypatching to assert:

- No arguments request length 8 and lowercase only.
- If any set flag is present, only explicit flags are passed to `generate_password()`.
- The generated password is printed once to stdout.
- Invalid lengths produce argparse error output and exit code `2`.

- [ ] **Step 6: Implement `main()`**

Parse arguments, determine whether any set flag was supplied, enable lowercase only when none were supplied, call `generate_password()`, convert its `ValueError` into `parser.error()`, print the result, and return `0`.

- [ ] **Step 7: Add the executable entry point**

Create `pw-gen.py` containing:

```python
#!/usr/bin/env python3

from password_generator import main


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 8: Run CLI tests and smoke checks**

Run:

```bash
uv run ruff format .
uv run ruff check --fix .
uv run ruff format --check .
uv run ruff check .
uv run pytest tests/test_password_generator.py -k "parser or main"
uv run pw-gen.py --help
uv run pw-gen.py
uv run pw-gen.py -l 12 -c -u -d -s
```

Expected: Ruff passes; pytest passes; help lists every flag; generated passwords have lengths 8 and 12 respectively.

- [ ] **Step 9: Commit the CLI**

```bash
git add password_generator.py pw-gen.py tests/test_password_generator.py
git commit -m "feat: add password generator CLI"
```

## Task 4: Add Clipboard Support

**Test owner:** Senior Test Engineer

**Implementation owner:** Senior Python Engineer

**Files:**
- Modify: `password_generator.py`
- Modify: `tests/test_password_generator.py`

- [ ] **Step 1: Write failing clipboard success tests**

Monkeypatch `pyperclip.copy` and `generate_password`, call `main(["--cb"])`, and assert:

- `pyperclip.copy()` receives the generated password exactly once.
- The same password is printed to stdout.
- `main()` returns `0`.

- [ ] **Step 2: Write failing clipboard error tests**

Make `pyperclip.copy()` raise `pyperclip.PyperclipException`. Assert that:

- `main()` returns `1`.
- stderr starts with `error: unable to copy password to clipboard:`.
- The password is not printed because the complete requested operation failed.

Also simulate `pyperclip` being unavailable and assert that:

- `main(["--cb"])` returns `1` with the same concise stderr prefix.
- `main([])` still succeeds without importing `pyperclip`.

- [ ] **Step 3: Run clipboard tests**

Run:

```bash
uv run pytest tests/test_password_generator.py -k clipboard
```

Expected: FAIL because clipboard handling is not implemented.

- [ ] **Step 4: Implement clipboard handling**

Import `pyperclip` lazily inside the `--cb` branch, call `pyperclip.copy(password)` before printing, and catch both `ImportError` and `pyperclip.PyperclipException`. Write the defined error message to stderr and return `1` on failure. Do not import or reference `pyperclip` when `--cb` is not requested.

- [ ] **Step 5: Verify clipboard behavior**

Run:

```bash
uv run ruff format .
uv run ruff check --fix .
uv run ruff format --check .
uv run ruff check .
uv run pytest tests/test_password_generator.py -k clipboard
```

Expected: Ruff passes and the clipboard pytest tests pass.

- [ ] **Step 6: Commit clipboard support**

```bash
git add password_generator.py tests/test_password_generator.py
git commit -m "feat: support copying passwords to clipboard"
```

## Task 5: Document and Verify Version 1

**Owner:** Senior Python Engineer

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Expand the README**

Document:

- Python 3.11+ and uv prerequisites.
- `uv sync --dev` installation.
- Both `python3 pw-gen.py` and `uv run pw-gen.py` invocation forms.
- Direct `python3 pw-gen.py` clipboard usage requires activating the environment created by uv; `uv run pw-gen.py --cb` resolves the dependency automatically.
- Every flag and its meaning.
- The default 8-character lowercase behavior.
- The requirement that length accommodate every selected set.
- Clipboard behavior and its `pyperclip` dependency.
- The complete example:

```bash
uv run pw-gen.py -l 12 -c -u -d -s --cb
```

- [ ] **Step 2: Run the complete automated suite**

Run:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

Expected: Ruff reports no formatting or lint issues and all pytest tests pass.

- [ ] **Step 3: Run final CLI acceptance checks**

Run:

```bash
uv run pw-gen.py
uv run pw-gen.py -l 12 -c -u -d -s
uv run pw-gen.py -l 3 -c -u -d -s
uv run pw-gen.py --help
```

Expected:

- The default command prints eight lowercase characters.
- The combined command prints 12 characters containing every selected set.
- The insufficient-length command exits with code `2` and a clear parser error.
- Help exits with code `0` and lists all documented flags.

- [ ] **Step 4: Commit documentation**

```bash
git add README.md
git commit -m "docs: document password generator usage"
```

## Task 6: Publish and Review the GitHub Pull Request

**Publishing owner:** Senior Python Engineer

**Review owner:** Senior Code Reviewer

- [ ] **Step 1: Confirm the feature branch is ready to publish**

The Senior Python Engineer runs:

```bash
git status --short
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

Expected: the worktree is clean, Ruff passes, and all pytest tests pass.

- [ ] **Step 2: Push the feature branch and open a GitHub pull request**

Push the current branch to `origin` and open a pull request whose description includes:

- A summary of the password generator behavior.
- The default 8-character lowercase behavior.
- The selected-set representation guarantee.
- CLI validation and clipboard failure behavior.
- The exact test and acceptance commands run.
- Confirmation that Ruff formatting and lint checks pass.
- A link or direct reference to `plan-password-generator.md`.

The PR must include all test, implementation, dependency, lockfile, and documentation commits from Tasks 1 through 5.

- [ ] **Step 3: Review plan coverage in the PR**

The Senior Code Reviewer inspects the pushed PR diff and checks that:

- Every flag and default in the prompt and this plan is implemented.
- Tests were written for defaults, each character set, combined sets, exclusions, invalid lengths, CLI parsing, help, output, clipboard success, and clipboard failure.
- Ruff is configured in `pyproject.toml` and is the only formatter and linter.
- Pytest is configured in `pyproject.toml` and is the test runner used throughout the PR.
- Production code uses `secrets` and never uses `random`.
- Every selected character set is guaranteed to appear.
- CLI exit codes, stdout, and stderr behavior match this plan.
- The dependency and README changes support both documented invocation forms.
- No unrelated changes or unplanned features are included.

- [ ] **Step 4: Independently verify the pushed PR**

From the reviewed PR branch, the Senior Code Reviewer runs:

```bash
uv sync --dev
uv run ruff format --check .
uv run ruff check .
uv run pytest
uv run pw-gen.py
uv run pw-gen.py -l 12 -c -u -d -s
uv run pw-gen.py -l 3 -c -u -d -s
uv run pw-gen.py --help
```

Expected: dependency installation succeeds, Ruff passes, all pytest tests pass, and every CLI result matches the acceptance criteria in Task 5.

- [ ] **Step 5: Resolve review findings**

For each reviewer finding:

- Test gaps return to the Senior Test Engineer, who adds a failing regression test and pushes the test commit.
- Implementation, security, dependency, or documentation defects return to the Senior Python Engineer, who fixes them and pushes the implementation commit.
- The responsible engineer runs Ruff formatting and linting, focused pytest tests, and the full pytest suite before pushing.
- The Senior Code Reviewer re-reviews the updated diff and reruns the relevant verification.

- [ ] **Step 6: Record the review verdict**

The Senior Code Reviewer records a passing verdict only when:

- Every requirement in this plan is represented by implementation and tests.
- Ruff formatting and lint checks, the complete pytest suite, and CLI acceptance checks pass on the pushed PR branch.
- All review findings are resolved.
- The PR diff contains no out-of-scope changes.

If repository policy requires approval from someone other than the author or automated reviewer, request that independent human approval after the passing verdict is recorded.

## Review Assumptions

- Version 1 is a non-interactive CLI with no configuration file, persistence, password-strength score, or GUI.
- Passwords are printed even when clipboard copying succeeds so the standard output contract remains consistent.
- Clipboard failure prevents printing and returns a nonzero status because the requested operation was not completed.
- Tests validate password properties instead of exact generated values.
- Implementation must not use `random`, which is unsuitable for password generation.
- Ruff is the required formatter and linter; pytest is the required test runner.
- The three agent roles remain separate throughout implementation and review to preserve independent test authorship and final verification.
- Agent work is sequential in the shared worktree to prevent concurrent edits, test runs, or commits from interfering with one another.
- A passing GitHub review verdict is a required completion gate; passing local tests alone does not complete the plan.
- Independent human approval is additionally required when repository policy does not permit the author or automated reviewer to approve the PR.
