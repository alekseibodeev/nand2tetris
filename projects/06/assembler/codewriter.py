from typing import Self, TextIO

class CodeWriter:
    def __init__(self: Self, stream: TextIO) -> None:
        self._stream = stream

    def write_address(self: Self, address: int) -> None:
        self._write_line(f"{address:016b}")

    def write_computation(
        self: Self, dest: str | None, comp: str, jump: str | None
    ) -> None:
        destb = self._code_dest(dest)
        compb = self._code_comp(comp)
        jumpb = self._code_jump(jump)
        self._write_line(f"111{compb}{destb}{jumpb}")

    def _code_dest(self: Self, dest: str | None) -> str:
        if not dest:
            return '000'
        A = int("A" in dest)
        D = int("D" in dest)
        M = int("M" in dest)
        return f"{A}{D}{M}"

    def _code_comp(self: Self, comp: str) -> str:
        return _COMP_MAP[comp]

    def _code_jump(self: Self, jump: str | None) -> str:
        if not jump:
            return "000"
        return _JUMP_MAP[jump]

    def _write_line(self: Self, msg: str) -> None:
        self._stream.write(msg + "\n")

_COMP_MAP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}

_JUMP_MAP = {
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}
