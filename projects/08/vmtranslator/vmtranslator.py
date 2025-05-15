#!/usr/bin/env python

import argparse
from pathlib import Path
from typing import Self
from parser import Parser
from codewriter import CodeWriter

class VMTranslator:
    def __init__(self: Self, path: Path) -> None:
        self._input_path = VMTranslator._get_input_paths(path)
        self._output_path = VMTranslator._get_output_path(path)

    def translate(self: Self) -> None:
        code = CodeWriter(self._output_path)

        if isinstance(self._input_path, Path):
            code.set_file_name(VMTranslator._get_file_name(self._input_path))
            parser = Parser(self._input_path)
            self._translate(parser, code)
            parser.close()
        else:
            for path in self._input_path:
                code.set_file_name(VMTranslator._get_file_name(path))
                parser = Parser(path)
                self._translate(parser, code)
                parser.close()

        code.write_end()
        code.close()

    def _translate(self: Self, parser: Parser, code: CodeWriter) -> None:
        while parser.has_more_lines():
            op = parser.get_op()

            if parser.is_pushpop():
                segment = parser.get_arg1()
                index = parser.get_arg2()
                code.write_pushpop(op, segment, index)
            elif parser.is_arithmetic():
                code.write_arithmetic(op)
            elif parser.is_label():
                label = parser.get_arg1()
                code.write_label(label)
            elif parser.is_goto():
                label = parser.get_arg1()
                code.write_goto(label)
            elif parser.is_if():
                label = parser.get_arg1()
                code.write_if(label)
            elif parser.is_function():
                function_name = parser.get_arg1()
                n_args = parser.get_arg2()
                code.write_function(function_name, n_args)
            elif parser.is_return():
                code.write_return()
            elif parser.is_call():
                function_name = parser.get_arg1()
                n_args = parser.get_arg2()
                code.write_call(function_name, n_args)

    @staticmethod
    def _get_file_name(path: Path) -> str:
        return path.name.removesuffix(".vm")

    @staticmethod
    def _get_input_paths(path: Path) -> Path | list[Path]:
        if path.is_file():
            return path.resolve()
        else:
            return [p.resolve() for p in path.glob("*.vm")]

    @staticmethod
    def _get_output_path(path: Path) -> Path:
        if path.is_file():
            return path.with_suffix(".asm").resolve()
        name = VMTranslator._get_file_name(path)
        return (path / name).with_suffix(".asm").resolve()

def validate_path(path_str: str) -> Path:
    path_suffix = ".vm"
    path = Path(path_str)

    if not path.exists():
        raise argparse.ArgumentTypeError(f"file '{path}' does not exist")
    if path.is_file() and path.suffix != path_suffix:
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
