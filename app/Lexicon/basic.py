"""
Podstawowy słownik programu, niedługo dojdzie do modyfikacji tego socketu, więc nie opisywałem.
"""
import typing as tp
from collections import namedtuple
from string import ascii_letters as alphabet
from functools import lru_cache
import re
from functools import reduce
import Lexicon.__utils__ as utils

SOCKET = 'Lexicon'
VERSION = '0.0.1'

TESTING = False

full_lexicon = dict(
    constants=(
        # AND
        ('^', 'and'),
        ('and', 'and'),
        ('&', 'and'),
        # OR
        ('v', 'or'),
        ('or', 'or'),
        ('|', 'or'),
        # NEGATION
        ('~', 'not'),
        ('not', 'not'),
        # IMPLICATION
        ('->', 'imp'),
        ('imp', 'imp'),
        # QUANTIFICATION
        ('A', 'forall'),
        ('/\\', 'forall'),
        ('forall', 'forall'),
        ('E', 'exists'),
        ('\\/', 'exists'),
        ('exists', 'exists'),
        
        # SEQUENT CALCULUS
        ('=>', 'turnstile'),
        (';', 'sep'),
        ('F', 'falsum')
    ),
    semantic=(
        # =, <, > and other things that need to carry semantics in proofs
    ),
    variables=(
        (r'[u-z]', 'indvar'),
        (r'[a-t]', 'constant'),
        (r'[P-Z]', 'predicate'),
        (r'[F-O]', 'function'),
        # Zero order logic
        (r'[p-z]', 'sentvar'),
    ),
)

full_lexicon['types'] = reduce(lambda x, y: x | y, ((
    {i[1] for i in value} for value in full_lexicon.values())), set())


def group_by_value(l: list[tuple[str, str]]) -> dict[str, list[str]]:
    """When given a list of (key, value) returns a dictionary, where keys are grouped by values"""
    allfound = {}
    for i in l:
        if i[0] in allfound:
            allfound[i[0]].append(i[1])
        else:
            allfound[i[0]] = [i[1]]
    return allfound


def letter_range(regex: str) -> tuple[int, int]:
    """For a regex given in lexicon.variables returns the indexes of first and last letter"""
    assert regex[1].islower() is regex[3].islower(
    ), "One letter is higher case and one is lower case"
    return alphabet.index(regex[1]), alphabet.index(regex[3])


def sign_list(type_: str) -> list[str]:
    """Zwraca listę potencjalnych znaków dla typów zmiennych (sentvar, predicate itp.)"""
    for letters, var_type in full_lexicon.get('variables'):
        if var_type == type_:
            break
    else:
        raise Exception("Taki typ nie został zdefiniowany")
    
    i, j = letter_range(letters)
    return list(alphabet[i:j])


def check_range(letter: str, indexA: int, indexB: int) -> bool:
    """Checks if letter's index is in <indexA, indexB>"""
    assert len(letter) == 1
    return (v := alphabet.index(letter)) >= indexA and v <= indexB


Lexicon = namedtuple(
    'Lexicon', ['pattern', 'defined', 'keywords', 'variables'])


@lru_cache(3)
def simplify_lexicon(used_tokens: frozenset[str], defined: frozenset[tuple[str, str]]) -> Lexicon:
    """Filters out patterns that aren't used, creates a regex pattern at Lexicon.pattern, returns a lexicon object"""
    lack = used_tokens - full_lexicon['types']
    if lack:
        raise utils.CompilerError(
            f"Lexicon lacks following types: {', '.join(lack)}")

    # Filtering
    filtered_def = list(filter(lambda x: x[1] in used_tokens, defined))
    filtered_keywords = list(filter(lambda x: x[1] in used_tokens, full_lexicon['constants'])) + list(
        filter(lambda x: x[1] in used_tokens, full_lexicon['semantic']))
    filtered_var = list(
        filter(lambda x: x[1] in used_tokens, full_lexicon['variables']))

    # Check for lexicon fullness
    assert len(filtered_keywords) > 0, "No keywords"
    assert any(filtered_var) or TESTING, "No variables"  # Turn off for testing

    # Check for duplicates
    dup_key = [i for i in group_by_value(
        filtered_keywords).items() if len(i[1]) > 1]
    if dup_key:
        raise utils.MultipleTypesError(dup_key)
    dup_var = [i for i in group_by_value(
        filtered_keywords).items() if len(i[1]) > 1]
    if dup_var:
        raise utils.MultipleTypesError(dup_var)

    # Prepare data
    dict_keys = {i[0]: f"{i[1]}_{i[0]}" for i in filtered_keywords}
    dict_def = {i[0]: f"{i[1]}_{i[0]}" for i in filtered_def}
    tup_variables = [(letter_range(i[0]), i[1]) for i in filtered_var]

    # Generate pattern
    in_pattern = [re.escape(i) for i in utils.NON_CONVERTIBLE] + [re.escape(i[0]) for i in filtered_def] + sorted(
        [re.escape(i[0]) for i in filtered_keywords], key=len, reverse=True) + [i[0] for i in filtered_var]
    pattern = re.compile("|".join(in_pattern))

    return Lexicon(pattern=pattern, defined=dict_def, keywords=dict_keys, variables=tup_variables)


def find_token(string: str, lex: Lexicon) -> str:
    """Finds the string in the lexicon and returns it

    :param string: Searched string
    :type string: str
    :param lex: Used lexicon object (generate with simplify_lexicon)
    :type lex: Lexicon
    :raises CompilerError: Raised if the string can't be properly tokenized
    :return: [type]_[string] or something from NON_CONVERTIBLE
    :rtype: str
    """
    # Check for NON_CONVERTIBLE
    if string in utils.NON_CONVERTIBLE:
        return string

    # Check if _ exists in string
    if '_' in string:
        raise utils.CompilerError(
            f'"{string}" contains "_", which is a reserved sign')

    # Check defined
    found = lex.defined.get(string, None)

    # Check keywords
    if not found:
        found = lex.keywords.get(string, None)

    # Check variables
    if not found:
        for i in lex.variables:
            if check_range(string, i[0][0], i[0][1]):
                found = "_".join((i[1], string))

    # Raise exception
    if not found:
        raise utils.CompilerError(f'Token not found for "{string}"')
    return found


def is_fully_tokenized(sent: utils.Sentence) -> bool:
    return all((any((j in i for j in ("_", *utils.NON_CONVERTIBLE))) for i in sent))


def tokenize(statement: str, used_tokens: tp.Iterable[str], defined: dict[str, str] = dict()) -> utils.Sentence:
    """Transforms the sentence into a list of tokens in the form of `type_lexem`

    :param statement: The statement to tokenize
    :type statement: str
    :param used_tokens: List of tokens used in this formal system (`FormalSystem.get_used_types`)
    :type used_tokens: tp.Iterable[str]
    :param defined: Variables defined by the user, defaults to dict()
    :type defined: dict[str, str], optional
    :raises CompilerError: The sentence wasn't tokenized 
    :return: Tokenized statement
    :rtype: utils.Sentence
    """

    # Getting the lexicon 
    dictionary = simplify_lexicon(frozenset(used_tokens), frozenset(defined.items()))
    
    # Find and get tokens
    sentence = dictionary.pattern.findall(statement)
    sentence = [find_token(lexem, dictionary) for lexem in sentence]

    # Additional check
    if not is_fully_tokenized(sentence):
        raise utils.CompilerError("System didn't fully tokenize the sentence")
    
    return sentence


def get_lexem(token: str) -> str:
    """Returns the lexem which was used to find the token"""
    if token in utils.NON_CONVERTIBLE:
        return token
    else:
        return token.split('_')[-1]


def get_type(token: str) -> str:
    """Returns the type of a token"""
    if token in utils.NON_CONVERTIBLE:
        return token
    else:
        return token.split('_')[0]


def join_to_string(sentence: utils.Sentence) -> str:
    """Writes the sentence as a string, where tokens are written as `<[token type]_[lexem]>`"""
    new = []
    for token in sentence:
        if token in utils.NON_CONVERTIBLE:
            new.append(token)
        else:
            new.append(f"<{token}>")
    return "".join(new)
