import sys

def print_error(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def print_usage():
    print("usage: ./assembler.py <path_to_file.asm>")

def exit_with_error(message: str) -> None:
        print_error(message)
        print_usage()
        sys.exit(1)
