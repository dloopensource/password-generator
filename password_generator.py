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
