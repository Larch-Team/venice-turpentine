import pytest

from venice_turpentine.core.token import Token
from venice_turpentine.lexers import BasicLex


@pytest.fixture
def lexer():
    return BasicLex.compile(use_language=("propositional", "uses negation"))


def token_from_string(token):
    if token in ["(", ")"]:
        return Token.literal(token)
    type_, token = token.split("_")
    return Token(type_, token)


def tokens_from_list(tokens):
    return [token_from_string(i) for i in tokens]


@pytest.mark.parametrize(
    "input_text, expected_tokens",
    [
        ("p or q", ["sentvar_p", "or_or", "sentvar_q"]),
        ("p and q", ["sentvar_p", "and_and", "sentvar_q"]),
        ("p imp q", ["sentvar_p", "imp_imp", "sentvar_q"]),
        ("not p", ["not_not", "sentvar_p"]),
    ],
)
def test_full_word(lexer, input_text, expected_tokens):
    assert lexer.tokenize(input_text) == tokens_from_list(expected_tokens)


@pytest.mark.parametrize(
    "input_text, expected_tokens",
    [
        ("p v q", ["sentvar_p", "or_v", "sentvar_q"]),
        ("p | q", ["sentvar_p", "or_|", "sentvar_q"]),
        ("p ^ q", ["sentvar_p", "and_^", "sentvar_q"]),
        ("p & q", ["sentvar_p", "and_&", "sentvar_q"]),
        ("p -> q", ["sentvar_p", "imp_->", "sentvar_q"]),
        ("~ p", ["not_~", "sentvar_p"]),
    ],
)
def test_full_symbol(lexer, input_text, expected_tokens):
    assert lexer.tokenize(input_text) == tokens_from_list(expected_tokens)


@pytest.mark.parametrize(
    "input_text, expected_tokens",
    [
        ("(p v q)", ["(", "sentvar_p", "or_v", "sentvar_q", ")"]),
        ("(p | q)", ["(", "sentvar_p", "or_|", "sentvar_q", ")"]),
        ("(p ^ q)", ["(", "sentvar_p", "and_^", "sentvar_q", ")"]),
        ("(p & q)", ["(", "sentvar_p", "and_&", "sentvar_q", ")"]),
        ("(p -> q)", ["(", "sentvar_p", "imp_->", "sentvar_q", ")"]),
        ("(~ p)", ["(", "not_~", "sentvar_p", ")"]),
    ],
)
def test_bracket(lexer, input_text, expected_tokens):
    assert lexer.tokenize(input_text) == tokens_from_list(expected_tokens)
