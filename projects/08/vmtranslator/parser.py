from pathlib import Path
from typing import Self, Iterator

class Parser:
    def __init__(self: Self, path: Path) -> None:
        self._stream = open(path)
        self._iterator = self._get_iterator()
        self._args = []

    def close(self: Self) -> None:
        self._stream.close()

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

    def is_label(self: Self) -> bool:
        return self.get_op() == "label"

    def is_goto(self: Self) -> bool:
        return self.get_op() == "goto"

    def is_if(self: Self) -> bool:
        return self.get_op() == "if-goto"

    def is_function(self: Self) -> bool:
        return self.get_op() == "function"

    def is_return(self: Self) -> bool:
        return self.get_op() == "return"

    def is_call(self: Self) -> bool:
        return self.get_op() == "call"

    def get_op(self: Self) -> str:
        return self._args[0]

    def get_arg1(self: Self) -> str:
        return self._args[1]

    def get_arg2(self: Self) -> int:
        return int(self._args[2])

    def _get_iterator(self: Self) -> Iterator[str]:
        for line in self._stream:
            cleaned = Parser._clean_line(line)
            if cleaned:
                yield cleaned

    @staticmethod
    def _clean_line(line: str) -> str:
        return line.split("//")[0].strip()
