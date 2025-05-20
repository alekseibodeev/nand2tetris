#!/usr/bin/env python

import argparse
from pathlib import Path
from typing import Self
from compilation_engine import CompilationEngine

class JackAnalyzer:
    def __init__(self: Self, path: Path) -> None:
        self._input_path = JackAnalyzer._get_input_path(path)

    def analyze(self: Self) -> None:
        input_path = self._input_path
        if isinstance(input_path, Path):
            output_path = self._get_output_path(input_path)
            CompilationEngine(input_path, output_path).compile()
        else:
            for path in input_path:
                output_path = self._get_output_path(path)
                CompilationEngine(path, output_path).compile()

    @staticmethod
    def _get_input_path(path: Path) -> Path | list[Path]:
        if path.is_file():
            return path.resolve()
        return [p.resolve() for p in path.glob("*.jack")]

    @staticmethod
    def _get_output_path(path: Path) -> Path:
        name = "_" + path.name
        return path.with_name(name).with_suffix(".xml")



def validate_path(path_str: str) -> Path:
    SUFFIX = ".jack"
    path = Path(path_str)

    if not path.exists():
        raise argparse.ArgumentTypeError(f"file '{path}' does not exist")
    if path.is_file() and path.suffix != SUFFIX:
        raise argparse.ArgumentTypeError(
            f"file extension must be '{SUFFIX}', but got '{path.suffix}'"
        )

    return path

def main():
    parser = argparse.ArgumentParser(
        description="Translate .jack code to token list in .xml format."
    )
    parser.add_argument(
        "path", type=validate_path, help="path to .jack file or directory"
    )
    args = parser.parse_args()
    JackAnalyzer(args.path).analyze()

if __name__ == "__main__":
    main()
