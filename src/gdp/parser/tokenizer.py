import re

TOKEN_REGEX = [
    ("KEYWORD", r"\b(Variable|Variables|Bounds|EndBounds|EndVar|Model|Solver|eqL|eq|fx|obj)\b"),
    ("NUMBER", r"\b\d+(\.\d+)?\b"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP", r"[=<>+\-*/()\[\],]"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
]

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


def tokenize(text):
    tokens = []
    for line in text.splitlines():
        pos = 0
        while pos < len(line):
            match = None
            for ttype, pattern in TOKEN_REGEX:
                regex = re.compile(pattern)
                match = regex.match(line, pos)
                if match:
                    value = match.group(0)
                    if ttype != "SKIP":
                        tokens.append(Token(ttype, value))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Unexpected character: {line[pos]}")
    return tokens
