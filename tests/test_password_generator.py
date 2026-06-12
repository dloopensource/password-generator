import string

import pytest

import password_generator
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


def test_parser_defaults_to_length_eight():
    arguments = password_generator.build_parser().parse_args([])

    assert arguments.length == 8


def test_parser_accepts_password_length():
    arguments = password_generator.build_parser().parse_args(["-l", "12"])

    assert arguments.length == 12


@pytest.mark.parametrize(
    ("flag", "destination"),
    [
        ("-c", "include_lowercase"),
        ("-u", "include_uppercase"),
        ("-d", "include_digits"),
        ("-s", "include_special"),
    ],
)
def test_parser_accepts_each_character_flag(flag, destination):
    arguments = password_generator.build_parser().parse_args([flag])

    assert getattr(arguments, destination) is True


def test_parser_accepts_all_character_flags():
    arguments = password_generator.build_parser().parse_args(["-c", "-u", "-d", "-s"])

    assert arguments.include_lowercase is True
    assert arguments.include_uppercase is True
    assert arguments.include_digits is True
    assert arguments.include_special is True


def test_parser_accepts_clipboard_flag():
    arguments = password_generator.build_parser().parse_args(["--cb"])

    assert arguments.copy_to_clipboard is True


def test_parser_help_lists_every_flag_and_exits_successfully(capsys):
    parser = password_generator.build_parser()

    with pytest.raises(SystemExit) as error:
        parser.parse_args(["--help"])

    assert error.value.code == 0
    help_output = capsys.readouterr().out
    for flag in ("-h", "--help", "-l", "-c", "-u", "-d", "-s", "--cb"):
        assert flag in help_output


def test_main_defaults_to_lowercase_only(monkeypatch):
    calls = []

    def fake_generate_password(**keyword_arguments):
        calls.append(keyword_arguments)
        return "password"

    monkeypatch.setattr(password_generator, "generate_password", fake_generate_password)

    assert password_generator.main([]) == 0
    assert calls == [
        {
            "length": 8,
            "include_lowercase": True,
            "include_uppercase": False,
            "include_digits": False,
            "include_special": False,
        }
    ]


def test_main_enables_only_explicit_character_flags(monkeypatch):
    calls = []

    def fake_generate_password(**keyword_arguments):
        calls.append(keyword_arguments)
        return "A0A0A0A0"

    monkeypatch.setattr(password_generator, "generate_password", fake_generate_password)

    assert password_generator.main(["-u", "-d"]) == 0
    assert calls == [
        {
            "length": 8,
            "include_lowercase": False,
            "include_uppercase": True,
            "include_digits": True,
            "include_special": False,
        }
    ]


def test_main_prints_generated_password_once_and_returns_success(capsys, monkeypatch):
    monkeypatch.setattr(
        password_generator,
        "generate_password",
        lambda **keyword_arguments: "generated-password",
    )

    result = password_generator.main([])

    assert result == 0
    captured = capsys.readouterr()
    assert captured.out == "generated-password\n"
    assert captured.err == ""


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["-l", "0"], "password length must be at least 1"),
        (
            ["-l", "1", "-c", "-u"],
            "password length must be at least the number of selected character sets",
        ),
    ],
)
def test_main_reports_invalid_lengths_as_cli_errors(arguments, message, capsys):
    with pytest.raises(SystemExit) as error:
        password_generator.main(arguments)

    assert error.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "error:" in captured.err
    assert message in captured.err
