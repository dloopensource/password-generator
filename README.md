# Password Generator

A secure command-line password generator built with Python's `secrets` module.

## Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)

## Installation

Install the runtime and development dependencies:

```bash
uv sync --dev
```

## Usage

Run the generator through uv:

```bash
uv run pw-gen.py
```

You can also invoke it directly:

```bash
python3 pw-gen.py
```

Generation without clipboard copying uses only the Python standard library.
Direct `python3 pw-gen.py --cb` usage requires activating the environment created
by uv first:

```bash
source .venv/bin/activate
python3 pw-gen.py --cb
```

Using `uv run pw-gen.py --cb` resolves the `pyperclip` dependency automatically.

## Options

| Flag | Meaning |
| --- | --- |
| `-h`, `--help` | Show help and exit. |
| `-l LENGTH` | Set the password length. The default is `8`. |
| `-c` | Include lowercase letters. |
| `-u` | Include uppercase letters. |
| `-d` | Include digits. |
| `-s` | Include special characters from Python's `string.punctuation`. |
| `--cb` | Copy the generated password to the clipboard. |

With no character-set flags, the generator creates an 8-character lowercase
password. Once any character-set flag is supplied, only the explicitly selected
sets are used.

Every selected character set is guaranteed to appear at least once. Password
length must therefore be at least `1` and at least the number of selected
character sets. Invalid lengths produce an error on stderr and exit with code
`2`.

## Clipboard

The `--cb` option copies the generated password with `pyperclip` and prints the
same password to stdout. If the dependency is unavailable or copying fails, the
command prints an error to stderr, does not print the password, and returns a
nonzero exit code.

## Example

Generate a 12-character password containing lowercase letters, uppercase
letters, digits, and special characters, then copy it to the clipboard:

```bash
uv run pw-gen.py -l 12 -c -u -d -s --cb
```
