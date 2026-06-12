import argparse
import secrets
import string


def generate_password(
    length: int = 8,
    include_lowercase: bool = True,
    include_uppercase: bool = False,
    include_digits: bool = False,
    include_special: bool = False,
) -> str:
    if length < 1:
        raise ValueError("password length must be at least 1")

    character_sets = [
        character_set
        for enabled, character_set in (
            (include_lowercase, string.ascii_lowercase),
            (include_uppercase, string.ascii_uppercase),
            (include_digits, string.digits),
            (include_special, string.punctuation),
        )
        if enabled
    ]

    if not character_sets:
        raise ValueError("at least one character set must be selected")
    if length < len(character_sets):
        raise ValueError(
            "password length must be at least the number of selected character sets"
        )

    characters = [secrets.choice(character_set) for character_set in character_sets]
    combined_pool = "".join(character_sets)
    characters.extend(
        secrets.choice(combined_pool) for _ in range(length - len(character_sets))
    )

    for index in range(len(characters) - 1, 0, -1):
        swap_index = secrets.randbelow(index + 1)
        characters[index], characters[swap_index] = (
            characters[swap_index],
            characters[index],
        )

    return "".join(characters)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        dest="length",
        type=int,
        default=8,
        help="Password length (default: 8)",
    )
    parser.add_argument(
        "-c",
        dest="include_lowercase",
        action="store_true",
        help="Include lowercase letters",
    )
    parser.add_argument(
        "-u",
        dest="include_uppercase",
        action="store_true",
        help="Include uppercase letters",
    )
    parser.add_argument(
        "-d",
        dest="include_digits",
        action="store_true",
        help="Include digits",
    )
    parser.add_argument(
        "-s",
        dest="include_special",
        action="store_true",
        help="Include special characters",
    )
    parser.add_argument(
        "--cb",
        dest="copy_to_clipboard",
        action="store_true",
        help="Copy the generated password to the clipboard",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    any_character_set_selected = any(
        (
            arguments.include_lowercase,
            arguments.include_uppercase,
            arguments.include_digits,
            arguments.include_special,
        )
    )

    try:
        password = generate_password(
            length=arguments.length,
            include_lowercase=(
                arguments.include_lowercase or not any_character_set_selected
            ),
            include_uppercase=arguments.include_uppercase,
            include_digits=arguments.include_digits,
            include_special=arguments.include_special,
        )
    except ValueError as error:
        parser.error(str(error))

    print(password)
    return 0
