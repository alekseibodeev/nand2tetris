#!/usr/bin/env python

import os
import sys

import parser
import codewriter
from utils import exit_with_error

def main():
    if len(sys.argv) != 2:
        exit_with_error("error: Wrong number of arguments")

    file_name = sys.argv[1]

    if not has_vm_extension(file_name):
        exit_with_error("error: Invalid file extension")

    in_file_path = os.path.abspath(file_name)

    if not os.path.exists(in_file_path):
        exit_with_error("error: File does not exist")

    out_file_path = vm_to_asm(in_file_path)
    module_name = get_file_name(out_file_path)
    label_index = 0 # unique id for conditional labels

    with open(in_file_path) as reader, open(out_file_path, "w") as writer:
        for line in reader:
            line = line.strip()

            if parser.is_empty(line) or parser.is_comment(line):
                continue

            args = parser.get_args(line)
            op = parser.get_op(args)

            if parser.is_push(op):
                arg1 = parser.get_arg1(args)
                arg2 = parser.get_arg2(args)
                writer.write(codewriter.write_push(arg1, arg2, module_name))
            elif parser.is_pop(op):
                arg1 = parser.get_arg1(args)
                arg2 = parser.get_arg2(args)
                writer.write(codewriter.write_pop(arg1, arg2, module_name))
            elif parser.is_binary_arithmetic(op):
                writer.write(codewriter.write_binary_arithmetic(op))
            elif parser.is_unary_arithmetic(op):
                writer.write(codewriter.write_unary_arithmetic(op))
            elif parser.is_comparison(op):
                writer.write(codewriter.write_comparison(op, label_index))
                label_index += 1

        writer.write(codewriter.write_end())



def get_file_name(file_path: str) -> str:
    start = file_path.rfind("/") + 1
    end = file_path.rfind(".")
    return file_path[start:end]

def remove_file_extension(file_path: str) -> str:
    i = file_path.rfind(".")
    return file_path[:i]

def vm_to_asm(file_path: str) -> str:
    return remove_file_extension(file_path) + ".asm"

def has_vm_extension(file_name: str) -> bool:
    return file_name.endswith(".vm")

if __name__ == "__main__":
    main()
