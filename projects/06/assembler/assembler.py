#!/usr/bin/env python

import argparse
from typing import Self
from pathlib import Path
from parser import Parser
from codewriter import CodeWriter
from table import Table

class HackAssembler:
    def __init__(self: Self, path: Path):
        self._input_path = path.resolve()
        self._output_path = self._get_output_path()
        self._input_stream = open(self._input_path)
        self._output_stream = open(self._output_path, "w")
        self._parser = Parser(self._input_stream)
        self._code = CodeWriter(self._output_stream)
        self._table = Table()

    def assemble(self: Self) -> None:
        self._mark_labels()
        self._parser.reset()
        self._assemble()
        self._close_streams()

    def _mark_labels(self: Self) -> None:
        line_number = 0
        parser = self._parser

        while parser.has_more_lines():
            parser.advance()

            if not parser.is_label():
                line_number += 1
            else:
                symbol = parser.get_symbol()
                self._table.add_entry(symbol, line_number)

    def _assemble(self: Self) -> None:
        parser = self._parser
        code = self._code
        table = self._table

        while parser.has_more_lines():
            parser.advance()

            if parser.is_label():
                continue
            if parser.is_address():
                symbol = parser.get_symbol()
                is_num = symbol.isnumeric()

                if not is_num and not table.contains(symbol):
                    table.add_entry(symbol)

                address = int(symbol) if is_num else table.get_address(symbol)
                code.write_address(address)
            else:
                dest = parser.get_dest()
                comp = parser.get_comp()
                jump = parser.get_jump()
                code.write_computation(dest, comp, jump)

    def _close_streams(self: Self) -> None:
        self._input_stream.close()
        self._output_stream.close()

    def _get_output_path(self: Self) -> Path:
        return self._input_path.with_suffix(".hack")

def validate_path(path_str: str) -> Path:
    path_suffix = ".asm"
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
        description="Translate Hack Assembly code to Binary instructions."
    )
    parser.add_argument("path", type=validate_path, help="Path to .asm file")
    args = parser.parse_args()
    HackAssembler(args.path).assemble()

if __name__ == "__main__":
    main()
