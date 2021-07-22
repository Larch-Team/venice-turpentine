"""
Nowy system definicji języka.
Syntax do dodawania nowych jednostek:
```

    Lex[TYP] = LEKSEMY

```

Możliwe jest też wykorzystywanie kontekstów zawartych w `__utils__.py` przez zapis:
```

    with KONTEKST(ARGUMENTY): 
        Lex[TYP] = LEKSEMY

```

"""
import Lexicon.__utils__ as utils

SOCKET = 'Lexicon'
VERSION = '0.0.1'

Lex = utils.Lexicon()



def get_lexicon() -> utils.Lexicon:
    return Lex