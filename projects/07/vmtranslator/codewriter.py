from typing import Self, TextIO

class CodeWriter:
    SEGMENT_MAP = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
        "pointer": 3,
        "temp": 5
    }

    def __init__(self: Self, stream: TextIO, file_name: str) -> None:
        self._stream = stream
        self._file_name = file_name
        self._label_index = 0

    def write_pushpop(self: Self, op: str, segment: str, index: int) -> None:
        if op == "push":
            self._write_push(segment, index)
        else:
            self._write_pop(segment, index)

    def write_arithmetic(self: Self, op: str) -> None:
        if op in {"add", "sub", "and", "or"}:
            self._write_binary_arithmetic(op)
        elif op in {"neg", "not"}:
            self._write_unary_arithmetic(op)
        else:
            self._write_comparison(op)

    def write_end(self: Self) -> None:
        self._write_lines(
            "(END)",
            "@END",
            "0;JMP"
        )

    def _write_push(self: Self, segment: str, index: int) -> None:
        if segment == "constant":
            self._write_lines(
                f"@{index}",
                "D=A"
            )
        elif segment == "static":
            self._write_lines(
                f"@{self._file_name}.{index}",
                "D=M"
            )
        else:
            self._resolve_address(segment, index)
            self._write_lines("D=M")

        self._write_lines(
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        )

    def _write_pop(self: Self, segment: str, index: int) -> None:
        if segment == "static":
            self._write_lines(f"@{self._file_name}.{index}")
        else:
            self._resolve_address(segment, index)

        self._write_lines(
            "D=A",
            "@R13",
            "M=D",
            "@SP",
            "AM=M-1",
            "D=M",
            "@R13",
            "A=M",
            "M=D"
        )

    def _write_binary_arithmetic(self: Self, op: str) -> None:
        ops = {"add": "+", "sub": "-", "and": "&", "or": "|"}
        self._write_lines(
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            f"M=M{ops[op]}D"
        )

    def _write_unary_arithmetic(self: Self, op: str) -> None:
        ops = {"neg": "-", "not": "!"}
        self._write_lines(
            "@SP",
            "A=M-1",
            f"M={ops[op]}M"
        )

    def _write_comparison(self: Self, op: str) -> None:
        jump = {"eq": "JEQ", "lt": "JLT", "gt": "JGT"}[op]
        label = f"COMP_{self._label_index}"
        self._label_index += 1

        self._write_lines(
            "@SP",
            "AM=M-1",
            "D=M",
            "A=A-1",
            "D=M-D",
            f"@{label}_TRUE",
            f"D;{jump}",
            "@SP",
            "A=M-1",
            "M=0",
            f"@{label}_END",
            "0;JMP",
            f"({label}_TRUE)",
            "@SP",
            "A=M-1",
            "M=-1",
            f"({label}_END)"
        )

    def _resolve_address(self: Self, segment: str, index: int) -> None:
        base = self.SEGMENT_MAP[segment]
        if isinstance(base, int):
            self._write_lines(f"@{base + index}")
        else:
            self._write_lines(
                f"@{base}",
                "D=M",
                f"@{index}",
                "A=D+A"
            )

    def _write_lines(self: Self, *lines: str) -> None:
        for line in lines:
            self._write_line(line)

    def _write_line(self: Self, line: str) -> None:
        self._stream.write(line + "\n")
