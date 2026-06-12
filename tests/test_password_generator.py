import string

import password_generator
import pytest
from password_generator import generate_password


def test_default_password_is_eight_lowercase_characters():
    password = generate_password()

    assert len(password) == 8
    assert all(character in string.ascii_lowercase for character in password)


@pytest.mark.parametrize(
    ("keyword_arguments", "selected_characters", "unselected_characters"),
    [
        (
            {"include_lowercase": True},
            string.ascii_lowercase,
            string.ascii_uppercase + string.digits + string.punctuation,
        ),
        (
            {"include_lowercase": False, "include_uppercase": True},
            string.ascii_uppercase,
            string.ascii_lowercase + string.digits + string.punctuation,
        ),
        (
            {"include_lowercase": False, "include_digits": True},
            string.digits,
            string.ascii_letters + string.punctuation,
        ),
        (
            {"include_lowercase": False, "include_special": True},
            string.punctuation,
            string.ascii_letters + string.digits,
        ),
    ],
    ids=["lowercase", "uppercase", "digits", "special"],
)
def test_password_uses_only_the_selected_character_set(
    keyword_arguments, selected_characters, unselected_characters
):
    password = generate_password(length=32, **keyword_arguments)

    assert len(password) == 32
    assert all(character in selected_characters for character in password)
    assert all(character not in unselected_characters for character in password)


def test_password_represents_every_selected_character_set(monkeypatch):
    def fake_choice(pool):
        representatives = {
            string.ascii_lowercase: "a",
            string.ascii_uppercase: "A",
            string.digits: "0",
            string.punctuation: "!",
        }
        return representatives.get(pool, "a")

    monkeypatch.setattr(password_generator.secrets, "choice", fake_choice)
    monkeypatch.setattr(
        password_generator.secrets,
        "randbelow",
        lambda upper_bound: upper_bound - 1,
    )

    password = generate_password(
        length=8,
        include_lowercase=True,
        include_uppercase=True,
        include_digits=True,
        include_special=True,
    )

    assert len(password) == 8
    assert any(character in string.ascii_lowercase for character in password)
    assert any(character in string.ascii_uppercase for character in password)
    assert any(character in string.digits for character in password)
    assert any(character in string.punctuation for character in password)


@pytest.mark.parametrize("length", [0, -1])
def test_password_rejects_lengths_below_one(length):
    with pytest.raises(ValueError) as error:
        generate_password(length=length)

    assert str(error.value) == "password length must be at least 1"


def test_password_rejects_length_smaller_than_selected_set_count():
    with pytest.raises(ValueError) as error:
        generate_password(
            length=2,
            include_lowercase=True,
            include_uppercase=True,
            include_digits=True,
        )

    assert str(error.value) == (
        "password length must be at least the number of selected character sets"
    )


def test_password_rejects_no_selected_character_sets():
    with pytest.raises(ValueError) as error:
        generate_password(
            include_lowercase=False,
            include_uppercase=False,
            include_digits=False,
            include_special=False,
        )

    assert str(error.value) == "at least one character set must be selected"


def test_password_allows_length_one_with_one_selected_set():
    password = generate_password(length=1)

    assert len(password) == 1
    assert password in string.ascii_lowercase


def test_password_allows_length_equal_to_selected_set_count():
    password = generate_password(
        length=4,
        include_lowercase=True,
        include_uppercase=True,
        include_digits=True,
        include_special=True,
    )

    assert len(password) == 4
    assert any(character in string.ascii_lowercase for character in password)
    assert any(character in string.ascii_uppercase for character in password)
    assert any(character in string.digits for character in password)
    assert any(character in string.punctuation for character in password)
