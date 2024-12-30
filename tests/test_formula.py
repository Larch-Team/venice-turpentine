import pytest

from venice_turpentine.core.formula import Formula
from venice_turpentine.core.token import Token
from venice_turpentine.formal_systems.debug import DebugFormalSystem

@pytest.mark.parametrize("original_str_formula, expected_precedence", [
    ("a and b or c", {1: 0.5, 3: 0.5}),
    ("a and neg c", {1: 0.5, 2: 0.75}),
    ("( a ) and ( b )", {3: 0.5}),
    ("a and b", {1: 0.5}),
    ("( a and b ) imp neg c", {2: 1.5, 5: 0.25, 6: 0.75}),
    ("a and neg ( neg b )", {1: 0.5, 2: 0.75, 4: 1.75}),
])    
def test_precedence(original_str_formula, expected_precedence):
    formula = Formula([Token.literal(i) for i in original_str_formula.split()], DebugFormalSystem())
    assert formula.precedence() == expected_precedence

@pytest.mark.parametrize("original_str_formula, expected_str_formula", [
    ("( a and ( b ) )", "a and ( b )"),
    ("( a and b )", "a and b"),
    ("( a and b ) or c", "( a and b ) or c"),
    ("( neg a )", "neg a"),
    ("( neg a ) and b", "( neg a ) and b"),
    ("( neg a ) and ( neg b )", "( neg a ) and ( neg b )"),
    ("( ( neg a ) and ( neg b ) )", "( neg a ) and ( neg b )"),
    ("( ( ( a ) ) )", "a"),
    ("( ( ( a ) or b ) ) and c", "( ( ( a ) or b ) ) and c"),
    ("( ( ( a ) or ( neg b ) ) )", "( a ) or ( neg b )"),
])
def test_reduceBrackets(original_str_formula, expected_str_formula):
    formula_original = Formula([Token.literal(i) for i in original_str_formula.split()], DebugFormalSystem())
    formula_expected = Formula([Token.literal(i) for i in expected_str_formula.split()], DebugFormalSystem())
    assert formula_original.reduceBrackets().getTypes() == formula_expected.getTypes()
    
@pytest.mark.parametrize("str_formula, connective_index", [
    ("a and b or c", 3),
    ("a and neg c", 1),
    ("( a ) and ( b )", 3),
    ("a and b", 1),
    ("neg neg c", 0),
    ("neg neg ( neg b )", 0),
    ("neg neg ( a or neg b )", 0),
    ("neg a or neg b )", 2),
    ("a", None)
])
def test_getMainConnective(str_formula, connective_index):
    formula = Formula([Token.literal(i) for i in str_formula.split()], DebugFormalSystem())
    assert formula.getMainConnective() == connective_index

@pytest.mark.parametrize("str_formula, index, expected_str_formula_left, expected_str_formula_right", [
    ("a and b or c", 3, "a and b", "c"),
    ("a and neg c", 1, "a", "neg c"),
    ("( a ) and ( b )", 3, "a", "b"),
    ("a and b", 1, "a", "b"),
    ("neg neg c", 0, None, "neg c"),
    ("neg neg ( neg b )", 0, None, "neg ( neg b )"),
    ("neg neg ( a or neg b )", 4, "neg neg ( a )", "neg b"),
    ("neg a or neg b", 2, "neg a", "neg b"),
    ("a", 1, "a", None)
])
def test_splitByIndex(str_formula, index, expected_str_formula_left, expected_str_formula_right):
    formula = Formula([Token.literal(i) for i in str_formula.split()], DebugFormalSystem())

    if expected_str_formula_left is None:
        expected_formula_left = None
    else:
        expected_formula_left = Formula([Token.literal(i) for i in expected_str_formula_left.split()], DebugFormalSystem()).getTypes()

    if expected_str_formula_right is None:
        expected_formula_right = None
    else:
        expected_formula_right = Formula([Token.literal(i) for i in expected_str_formula_right.split()], DebugFormalSystem()).getTypes()

    formula_left, formula_right = formula.splitByIndex(index)
    
    # ifs are for managing None values
    if expected_formula_left is None:
        assert formula_left is None
    else:
        assert formula_left.getTypes() == expected_formula_left
    
    if expected_formula_right is None:
        assert formula_right is None
    else:
        assert formula_right.getTypes() == expected_formula_right

@pytest.mark.parametrize("str_formula, expected_connective, expected_left_result, expected_right_result", [
    ("a and b or c", "or", "a and b", "c"),
    ("a and neg c", "and", "a", "neg c"),
    ("( a ) and ( b )", "and", "a", "b"),
    ("a and b imp c", "imp", "a and b", "c"),
    ("neg neg c", "neg", None, "neg c"),
    ("neg neg ( neg b )", "neg", None, "neg ( neg b )"),
    ("neg neg ( a ) or neg b", "or", "neg neg ( a )", "neg b"),
    ("neg a or neg b", "or", "neg a", "neg b"),
    ("neg ( a or b )", "neg", None, "a or b"),
    ("a", None, None, None),
    ("a and b imp c and d", "imp", "a and b", "c and d"),
    ("a and b imp c and d", "imp", "a and b", "c and d"),
])
def test_getComponents(str_formula, expected_connective, expected_left_result, expected_right_result):
    formula = Formula([Token.literal(i) for i in str_formula.split()], DebugFormalSystem())

    if expected_left_result is None:
        expected_formula_left = None
    else:
        expected_formula_left = Formula([Token.literal(i) for i in expected_left_result.split()], DebugFormalSystem()).getTypes()

    if expected_right_result is None:
        expected_formula_right = None
    else:
        expected_formula_right = Formula([Token.literal(i) for i in expected_right_result.split()], DebugFormalSystem()).getTypes()

    connective_result, (formula_left, formula_right) = formula.getComponents()

    # ifs are for managing None values
    if expected_connective is None:
        assert connective_result is None
    else:
        assert expected_connective == connective_result.type_

    if expected_formula_left is None:
        assert formula_left is None
    else:
        assert formula_left.getTypes() == expected_formula_left

    if expected_formula_right is None:
        assert formula_right is None
    else:
        assert formula_right.getTypes() == expected_formula_right
