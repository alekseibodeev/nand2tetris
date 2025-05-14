#!/usr/bin/env python

import argparse
from pathlib import Path
from typing import Self
from parser import Parser
from codewriter import CodeWriter

class VMTranslator:
    def __init__(self: Self, path: Path) -> None:
        self._file_name = path.name
        self._input_path = path.resolve()
        self._output_path = self._get_output_path()
        self._input_stream = open(self._input_path)
        self._output_stream = open(self._output_path, "w")
        self._parser = Parser(self._input_stream)
        self._code = CodeWriter(self._output_stream, self._file_name)

    def translate(self: Self) -> None:
        self._translate()
        self._close_streams()

    def _translate(self: Self) -> None:
        parser = self._parser
        code = self._code

        while parser.has_more_lines():
            op = parser.get_op()

            if parser.is_pushpop():
                segment = parser.get_arg1()
                index = parser.get_arg2()
                code.write_pushpop(op, segment, index)
            elif parser.is_arithmetic():
                code.write_arithmetic(op)

        code.write_end()

    def _close_streams(self: Self) -> None:
        self._input_stream.close()
        self._output_stream.close()

    def _get_output_path(self: Self) -> Path:
        return self._input_path.with_suffix(".asm")

def validate_path(path_str: str) -> Path:
    path_suffix = ".vm"
    path = Path(path_str)

    if not path.exists():
        raise argparse.ArgumentTypeError(f"file '{path}' does not exist")
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"'{path}' is not a file")
    if path.suffix != path_suffix:
        raise argparse.ArgumentTypeError(
            f"file extension must be '{path_suffix}', but got '{path.suffix}'"
        )

    return path

def main():
    parser = argparse.ArgumentParser(
        description="Translate VM code to Hack assembly."
    )
    parser.add_argument("path", type=validate_path, help="Path to .vm file")
    args = parser.parse_args()
    VMTranslator(args.path).translate()

if __name__ == "__main__":
    main()
