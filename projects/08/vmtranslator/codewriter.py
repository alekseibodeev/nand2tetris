from pathlib import Path
from typing import Self

class CodeWriter:
    SEGMENT_MAP = {
        "local": "LCL",
        "argument": "ARG",
        "this": "THIS",
        "that": "THAT",
        "pointer": 3,
        "temp": 5
    }

    def __init__(self: Self, path: Path) -> None:
        self._stream = open(path, "w")
        self._file_name = ""
        self._function_name = ""
        self._label_index = 0
        self._call_index = 0
        self._bootstrap()

    def set_file_name(self: Self, file_name: str) -> None:
        print(f"Translating '{file_name}'...")
        self._file_name = file_name

    def close(self: Self) -> None:
        self._stream.close()

    def _bootstrap(self: Self) -> None:
        self._write_lines(
            "// Bootstrap code",
            "// =============================================",
            "",
            "// Initialize stack pointer to 256",
            "@256",
            "D=A",
            "@SP",
            "M=D",
            "",
            "// Call Sys.init",
            "// =============================================",
            "",
            "// Push return address",
            "@BOOTSTRAP_RETURN",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1",
            "",
        )
        self._save_caller_frame()
        self._reposition_arg(0)
        self._reposition_local()
        self._write_lines(
            "// Transfer control to Sys.init",
            "@Sys.init",
            "0;JMP",
            "",
            "// Return address label",
            "(BOOTSTRAP_RETURN)",
            "",
        )

    def _save_caller_frame(self: Self) -> None:
        self._write_line("// Save caller's frame")

        for label in ["LCL", "ARG", "THIS", "THAT"]:
            self._write_lines(
                f"// Save caller's {label}",
                f"@{label}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1",
                ""
            )

    def _reposition_arg(self: Self, n_args: int) -> None:
        self._write_lines(
            "// Reposition ARG (ARG = SP - 5 - n_args)",
            "@SP",
            "D=M",
            f"@{5 + n_args}",
            "D=D-A",
            "@ARG",
            "M=D",
            "",
        )

    def _reposition_local(self: Self) -> None:
        self._write_lines(
            "// Reposition LCL (LC = SP)",
            "@SP",
            "D=M",
            "@LCL",
            "M=D",
            "",
        )

    def write_pushpop(self: Self, op: str, segment: str, index: int) -> None:
        self._write_comment(op, segment, str(index))
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

    def write_label(self: Self, label: str) -> None:
        self._write_comment("label", label)
        self._write_line(f"({self._get_label(label)})")

    def write_goto(self: Self, label: str) -> None:
        self._write_comment("goto", label)
        self._write_lines(
            f"@{self._get_label(label)}",
            "0;JMP"
        )

    def write_if(self: Self, label: str) -> None:
        self._write_comment("if-goto", label)
        self._write_lines(
            "@SP",
            "AM=M-1",
            "D=M",
            f"@{self._get_label(label)}",
            "D;JNE"
        )

    def write_function(self: Self, name: str, n_args: int) -> None:
        self._write_comment("function", name, str(n_args))
        self._function_name = name
        self._call_index = 0

        self._write_lines(f"({name})")
        
        for _ in range(n_args):
            self._write_lines(
                "@SP",
                "A=M",
                "M=0",
                "@SP",
                "M=M+1"
            )

    def write_call(self: Self, name: str, n_args: int) -> None:
        self._write_comment("call", name, str(n_args))
        return_label = self._get_return_label()

        self._write_lines(
            f"// Call {name}",
            "// =============================================",
            "",
            "// Push return address",
            f"@{return_label}",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        )
        self._save_caller_frame()
        self._reposition_arg(n_args)
        self._reposition_local()
        self._write_lines(
            f"// Transfer control to {name}",
            f"@{name}",
            "0;JMP",
            "",
            "// Return address label",
            f"({return_label})"
        )

    def write_return(self: Self) -> None:
        self._write_lines(
            "// Return",
            "",
            "// Frame = LCL",
            "@LCL",
            "D=M",
            "// RetAddr = *(Frame - 5)",
            "@5",
            "A=D-A",
            "D=M",
            "@R13", # save return address in @R13
            "M=D",
        )
        self._write_lines(
            "// *ARG = pop()",
            "@SP",
            "A=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D",
            "// SP = ARG + 1",
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D",
        )

        for i, c in enumerate(["THAT" ,"THIS", "ARG", "LCL"]):
            self._write_lines(
                "@LCL",
                "D=M",
                f"@{i+1}",
                "A=D-A",
                "D=M",
                f"@{c}",
                "M=D"
            )

        self._write_lines(
            "@R13",
            "A=M",
            "0;JMP"
        )

    def write_end(self: Self) -> None:
        self._write_comment("end")
        self._write_lines(
            "(END)",
            "@END",
            "0;JMP"
        )

    def _get_label(self: Self, label: str) -> str:
        return f"{self._function_name}${label}"

    def _get_return_label(self: Self) -> str:
        label = f"{self._function_name}$ret.{self._call_index}"
        self._call_index += 1
        return label

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
        )

        if op == "sub":
            self._write_line("M=M-D")
        else:
            self._write_line(f"M=D{ops[op]}M")

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

    def _write_comment(self: Self, *args: str) -> None:
        self._write_line(f"// {" ".join(args)}")
