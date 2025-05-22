from pathlib import Path
from typing import Self

class VMWriter:
    def __init__(self: Self, path: Path) -> None:
        self._stream = open(path, "w")

    def close(self: Self) -> None:
        self._stream.close()

    def write_push(self: Self, segment: str, index: int) -> None:
        self._writeline(f"push {segment} {index}")

    def write_pop(self: Self, segment: str, index: int) -> None:
        self._writeline(f"pop {segment} {index}")

    def write_arithmetic(self: Self, command: str) -> None:
        self._writeline(command)

    def write_label(self: Self, label: str) -> None:
        self._writeline(f"label {label}")

    def write_goto(self: Self, label: str) -> None:
        self._writeline(f"goto {label}")

    def write_if(self: Self, label: str) -> None:
        self._writeline(f"if-goto {label}")

    def write_call(self: Self, label: str, n: int) -> None:
        self._writeline(f"call {label} {n}")

    def write_function(self: Self, label: str, n: int) -> None:
        self._writeline(f"function {label} {n}")

    def write_return(self: Self) -> None:
        self._writeline("return")

    def _writeline(self: Self, text: str) -> None:
        self._stream.write(text + "\n")
