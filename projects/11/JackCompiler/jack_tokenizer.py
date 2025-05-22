from pathlib import Path
from typing import Self
import re

class JackTokenizer:
    def __init__(self: Self, path: Path) -> None:
        self._tokens = JackTokenizer._tokenize(path)
        self._index = -1

    def has_more_tokens(self: Self) -> bool:
        return self._index + 1 < len(self._tokens)

    def next(self: Self) -> None:
        self._index += 1

    def previous(self: Self) -> None:
        self._index -= 1

    def is_keyword(self: Self) -> bool:
        return self._get_token() == "KEYWORD"

    def is_identifier(self: Self) -> bool:
        return self._get_token() == "IDENTIFIER"

    def is_symbol(self: Self) -> bool:
        return self._get_token() == "SYMBOL"

    def is_int(self: Self) -> bool:
        return self._get_token() == "INT_CONST"

    def is_string(self: Self) -> bool:
        return self._get_token() == "STRING_CONST"

    def token_type(self: Self) -> str:
        return self._get_token()

    def keyword(self: Self) -> str:
        return self._get_value()

    def symbol(self: Self) -> str:
        return self._get_value()
    
    def identifier(self: Self) -> str:
        return self._get_value()

    def int_val(self: Self) -> int:
        return int(self._get_value())

    def string_val(self: Self) -> str:
        return self._get_value()[1:-1]

    def _get_token(self: Self) -> str:
        return self._tokens[self._index][0]

    def _get_value(self: Self) -> str:
        return self._tokens[self._index][1]

    @staticmethod
    def _tokenize(path: Path) -> list[tuple[str, str]]:
        keywords = {
            "class", "constructor", "function", "method", "field",
            "static", "var", "int", "char", "boolean", "void", "true",
            "false", "null", "this", "let", "do", "if", "else",
            "while", "return"
        }
        token_specification = [
            ("COMMENT", r"/\*(?s:.*?)\*/|//.+\n"),
            ("STRING_CONST", r"\".*\""),
            ("IDENTIFIER", r"[_A-Za-z][_A-Za-z0-9]*"),
            ("INT_CONST", r"\d+"),
            ("SYMBOL", r"\S")
        ]
        token_regex = "|".join(f"(?P<{n}>{p})" for n, p in token_specification)
        tokens = []

        with open(path) as stream:
            code = stream.read()
            for mo in re.finditer(token_regex, code):
                kind = mo.lastgroup
                value = mo.group()

                if kind == "IDENTIFIER" and value in keywords:
                    tokens.append(("KEYWORD", value))
                elif kind != "COMMENT":
                    tokens.append((kind, value))

        return tokens
