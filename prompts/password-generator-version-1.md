# Objective
Create a plan inside plan-password-generator.md for a password generator with Python. 

## Flags
- `--help`: Show help message and exit
- `-l`: Length of the password
- `-c`: Include lowercase letters
- `-u`: Include uppercase letters
- `-d`: Include digits
- `-s`: Include special characters
- `--cb`: Copy the generated password to the clipboard (requires `pyperclip` library)

## Example
Run the script with `python3 pw-gen.py` or `uv run pw-gen.py`.

To create a password with 12 characters, including lowercase letters, uppercase letters, digits, special characters, and copy it to the clipboard, use:
`uv run pw-gen -l 12 -c -u -d -s --cb`




