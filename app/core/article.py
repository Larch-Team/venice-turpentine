from html.parser import HTMLParser
import os
from typing import NewType, Optional

class _Parser(HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.id_stack = []
        self.index_stack = []
        self.ranges = {}
        
    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if not attrs:
            self.id_stack.append(None)
            self.index_stack.append(self.getpos())
            return
        keys, vals = zip(*attrs)
        try:
            index = keys.index('id')
        except ValueError:
            self.id_stack.append(None)
        else:
            self.id_stack.append(vals[index])
        self.index_stack.append(self.getpos())
        
    def handle_endtag(self, tag: str) -> None:
        id_val = self.id_stack.pop()
        index = self.index_stack.pop()
        l, i = self.getpos()
        if id_val:
            self.ranges[id_val] = index, (l, i+len(tag)+3) # i (długość linii przed końcem) + len(tag) (długość tagu) + 3 ("</>")
            
    def handle_startendtag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if not attrs:
            return
        keys, vals = zip(*attrs)
        try:
            index = keys.index('id')
        except ValueError:
            return
        l, i = self.getpos()
        self.ranges[vals[index]] = (l, i), (l, i+len(self.get_starttag_text()))

_Article = NewType('_Article', object)

class Article(object):
    
    @staticmethod
    def read(directory: str, *files: str) -> dict[str, _Article]:
        d = {}
        files = list(files)
        while files:
            f_name = files.pop(0)
            file = f'{directory}/{f_name}'
            if os.path.isdir(file):
                files.extend([f'{f_name}/{i}' for i in os.listdir()])
            elif os.path.isfile(file) and f_name.endswith('.html'):
                d[f_name[:-5]] = Article(file)
            else:
                FileNotFoundError("There is no file with this name in the given directory")
        return d
    
    def __init__(self, file: str) -> None:
        super().__init__()
        self.file = file
        self.parts = self.read_parts()
        
    def read_parts(self) -> dict[str, tuple[tuple[int, int], tuple[int, int]]]:
        parser = _Parser()
        with open(self.file, encoding='utf8') as f:
            parser.feed(f.read())
        return parser.ranges
    
    def __getitem__(self, part: str) -> Optional[str]:
        if not isinstance(part, str):
            return None
        start, end = self.parts[part]
        start_line, start_pos = start
        end_line, end_pos = end
        
        with open(self.file, encoding='utf8') as f:
            lines = f.readlines()[start_line-1:end_line]
        lines[0] = lines[0][start_pos:]
        lines[-1] = lines[-1][:end_pos]
        
        return "".join(lines).strip('\n ')
    
    def text(self) -> str:
        with open(self.file, encoding='utf8') as f:
            t = f.read()
        return t