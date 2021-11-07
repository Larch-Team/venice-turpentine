import plugins.Formal.__utils__ as utils
from sentence import Sentence

@utils.Modifier
def convert_from_signed(s: Sentence):
    if s[0].startswith('signtrue'):
        return s[1:]
    elif s[0].startswith('signfalse'):
        return utils.add_prefix(s[1:], 'not')
    else:
        return s
    
@utils.Modifier
def convert_to_signed(s: Sentence):
    conn, a = s.getComponents()
    if a is None:
        return [s.generate('signtrue')]+s.reduceBrackets()
    else:
        (_, form) = a
    if conn.startswith('not_'):
        return [s.generate('signfalse')]+form.reduceBrackets()
    else:
        return [s.generate('signtrue')]+s.reduceBrackets()