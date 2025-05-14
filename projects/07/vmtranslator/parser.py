from typing import Self, TextIO, Iterator

class Parser:
    def __init__(self: Self, stream: TextIO) -> None:
        self._stream = stream
        self._iterator = self._get_iterator()
        self._args = []

    def has_more_lines(self: Self) -> bool:
        try:
            line = next(self._iterator)
            self._args = line.split(" ")
            return True
        except StopIteration:
            return False

    def is_pushpop(self: Self) -> bool:
        return self.get_op() in {"push", "pop"}

    def is_arithmetic(self: Self) -> bool:
        return self.get_op() in {"add" , "sub", "neg",
                                 "and", "or", "not",
                                 "eq", "lt", "gt"}

    def get_op(self: Self) -> str:
        return self._args[0]

    def get_arg1(self: Self) -> str:
        return self._args[1]

    def get_arg2(self: Self) -> int:
        return int(self._args[2])

    def _get_iterator(self: Self) -> Iterator[str]:
        for line in self._stream:
            cleaned = Parser._clean_line(line)
            if not Parser._is_empty(cleaned) and not Parser._is_comment(cleaned):
                yield cleaned

    @staticmethod
    def _is_empty(line: str) -> bool:
        return line == ""

    @staticmethod
    def _is_comment(line: str) -> bool:
        return line.startswith("//")

    @staticmethod
    def _clean_line(line: str) -> str:
        return line.strip()
