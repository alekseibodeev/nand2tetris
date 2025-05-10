#!/usr/bin/env python

import os
import sys
from typing import TextIO
import parser
import code_translator as code
from table import init_table
from utils import exit_with_error

def main():
    if len(sys.argv) != 2:
        exit_with_error("error: Wrong number of arguments")

    file_name = sys.argv[1]

    if not has_asm_extension(file_name):
        exit_with_error("error: Wrong file extension")

    in_file_path = os.path.abspath(file_name)

    if not os.path.exists(in_file_path):
        exit_with_error("error: File does not exist")

    out_file_path = asm_to_hack(in_file_path)
    symbol_table = init_table()

    with open(in_file_path) as reader, open(out_file_path, "w") as writer:
        populate_table_with_labels(reader, symbol_table)
        reset_stream(reader)
        translate_to_binary(reader, writer, symbol_table)

def populate_table_with_labels(reader: TextIO, table: dict[str, int]) -> None:
    """Read input stream and populate symbol's table with label addresses"""
    line_number = 0

    for line in reader:
        line = line.strip()
        if line == "" or parser.is_comment(line):
            continue
        if not parser.is_label(line):
            line_number += 1
        else:
            symbol = parser.get_symbol_from_label(line)
            table[symbol] = line_number

def translate_to_binary(reader: TextIO, writer: TextIO, table: dict[str, int]) -> None:
    """Translate each line in reader to binary command and write to writer."""
    symbol_address = 16

    for line in reader:
        line = parser.remove_spaces(line.strip())
        if line == "" or parser.is_comment(line) or parser.is_label(line):
            continue
        if parser.is_address(line):
            symbol = parser.get_symbol_from_address(line)
            is_numeric = symbol.isnumeric()

            if not is_numeric and symbol not in table:
                table[symbol] = symbol_address
                symbol_address += 1

            address = int(symbol) if is_numeric else table[symbol]
            writer.write(code.address_to_bin(address) + "\n")
        else:
            dest = parser.get_dest(line)
            comp = parser.get_comp(line)
            jump = parser.get_jump(line)
            dest_bin = code.dest_to_bin(dest)
            comp_bin = code.comp_to_bin(comp)
            jump_bin = code.jump_to_bin(jump)
            writer.write(f"111{comp_bin}{dest_bin}{jump_bin}\n")

def reset_stream(stream: TextIO) -> None:
    stream.seek(0)

def has_asm_extension(file_name: str) -> bool:
    return file_name.endswith(".asm")

def remove_file_extension(file_path: str) -> str:
    """Remove file extension.

    Assume file_path always has extension specified
    """
    i = file_path.rfind(".")
    return file_path[:i]

def asm_to_hack(file_path: str) -> str:
    """Convert file extension from asm to hack

    Assume file_path has .asm extension
    """
    return remove_file_extension(file_path) + ".hack"

if __name__ == "__main__":
    main()
