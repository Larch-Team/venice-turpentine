from string import Template as _Template
from typing import Any as _Any, Union as _Union

class Close(object):
    """
    Stempel przybijany na zamkniętą gałąź
    
    https://www.notion.so/szymanski/Zamykanie-ga-zi-53249279f1884ab4b6f58bbd6346ec8d
    """


    def __init__(self, success: bool, text: str, text_template: _Union[str, _Template] = None) -> None:
        """Stempel przybijany na zamkniętą gałąź

        :param success: Czy system powinien traktować takie zamknięcie jako krok do skończenia dowodu
        :type success: bool
        :param text: Zapis wyświetlany użytkownikowi przy zamkniętej gałęzi
        :type text: str
        :param text_template: Wzór do wypełnienia i wyświetlenia użytkownikowi (pozwala przykładowo na zapis "XXX ([numer zdania], [numer zdania])"), defaults to None
        :type text_template: Template, optional
        """
        super().__init__()
        self.text = text
        if text_template is None or isinstance(text_template, _Template):
            self.template = text_template
        else:
            self.template = _Template(text_template)
        self.success = success

    def __call__(self, **kwds: _Any):
        if not self.template:
            raise Exception("Nie możesz użyć wzorca, jeżeli nie został on podany")
        return Close(self.success, self.template.substitute(kwds))
    
    def __str__(self) -> str:
        return self.text


Emptiness = Close(False, "---")
Contradiction = Close(True, "XXX", "XXX ($sentID1, $sentID2)")
LoopCheck = Close(False, "...")
Axiom = Close(True, 'Ax')
Falsum = Close(True, 'Falsum')