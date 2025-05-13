from typing import Iterator, Self, TextIO

class Parser:
    def __init__(self: Self, stream: TextIO) -> None:
        self._stream = stream
        self._iterator = self._create_iterator()
        self._line = ""
        self._next_line = ""

    def reset(self: Self) -> None:
        self._stream.seek(0)
        self._iterator = self._create_iterator()
        self._line = ""
        self._next_line = ""

    def _create_iterator(self: Self) -> Iterator[str]:
        for line in self._stream:
            cleaned = Parser._clean_line(line)
            if not Parser._is_empty(cleaned) and not Parser._is_comment(cleaned):
                yield cleaned

    def has_more_lines(self: Self) -> bool:
        try:
            self._next_line = next(self._iterator)
            return True
        except StopIteration:
            return False

    def advance(self: Self) -> None:
        self._line = self._next_line

    @staticmethod
    def _is_empty(line: str) -> bool:
        return line == ""

    @staticmethod
    def _is_comment(line: str) -> bool:
        return line.startswith("//")

    def is_address(self: Self) -> bool:
        return self._line.startswith("@")

    def is_label(self: Self) -> bool:
        line = self._line
        return line.startswith("(") and line.endswith(")")

    def get_symbol(self: Self) -> str:
        if self.is_address():
            return self._line[1:]
        else:
            return self._line[1:-1]

    def get_dest(self: Self) -> str | None:
        line = self._line
        i = line.find("=")
        return line[:i] if i >= 0 else None

    def get_comp(self: Self) -> str:
        line = self._line
        i = self._get_comp_pivot()
        return line[i+1:] if line[i] == "=" else line[:i]

    def get_jump(self: Self) -> str | None:
        line = self._line
        i = line.find(";")
        return line[i+1:] if i >= 0 else None
        
    @staticmethod
    def _clean_line(line: str) -> str:
        return line.strip().replace(" ", "")

    def _get_comp_pivot(self: Self) -> int:
        for i, c in enumerate(self._line):
            if c in ["=", ";"]:
                return i
        return -1
