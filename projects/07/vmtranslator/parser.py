def is_comment(line: str) -> bool:
    return line.startswith("//")

def is_empty(line: str) -> bool:
    return line == ""

def get_args(line: str) -> list[str]:
    return line.split(" ")

def get_op(args: list[str]) -> str:
    return args[0]

def get_arg1(args: list[str]) -> str:
    return args[1]

def get_arg2(args: list[str]) -> int:
    return int(args[2])

def is_binary_arithmetic(op: str) -> bool:
    return op in ["add", "sub", "and", "or"]

def is_unary_arithmetic(op: str) -> bool:
    return op in ["neg", "not"]

def is_comparison(op: str) -> bool:
    return op in ["eq", "lt", "gt"]

def is_push(op: str) -> bool:
    return op == "push"

def is_pop(op: str) -> bool:
    return op == "pop"
