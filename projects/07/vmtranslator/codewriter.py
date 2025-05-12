SEGMENTS = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT"
}

def write_push(seg: str, i: int, file: str) -> str:
    stack = []

    # setup D Register with value to push
    if seg in ["local", "argument", "this", "that"]:
        stack.append(f"@{i}")
        stack.append("D=A")
        stack.append(f"@{SEGMENTS[seg]}")
        stack.append("A=M")
        stack.append("A=D+A")
        stack.append("D=M")
    elif seg == "pointer":
        if i == 0:
            stack.append("@THIS")
            stack.append("D=M")
        else:
            stack.append("@THAT")
            stack.append("D=M")
    elif seg == "temp":
        stack.append(f"@{5 + i}")
        stack.append("D=M")
    elif seg == "constant":
        stack.append(f"@{i}")
        stack.append("D=A")
    else:
        stack.append(f"@{file}.{i}")
        stack.append("D=M")

    # push value onto stack
    stack.append("@SP")
    stack.append("A=M")
    stack.append("M=D")
    stack.append("@SP")
    stack.append("M=M+1\n")

    return "\n".join(stack)

def write_pop(seg: str, i: int, file: str) -> str:
    stack = []

    # setup destination address
    if seg in ["local", "argument", "this", "that"]:
        stack.append(f"@{i}")
        stack.append("D=A")
        stack.append(f"@{SEGMENTS[seg]}")
        stack.append("A=M")
        stack.append("A=D+A")
    elif seg == "pointer":
        if i == 0:
            stack.append("@THIS")
        else:
            stack.append("@THAT")
    elif seg == "temp":
        stack.append(f"@{5 + i}")
    else:
        stack.append(f"@{file}.{i}")

    # store destination address in R13
    stack.append("D=A")
    stack.append("@13")
    stack.append("M=D")

    # pop value from stack
    stack.append("@SP")
    stack.append("M=M-1")
    stack.append("A=M")
    stack.append("D=M")

    # write popped value to destination
    stack.append("@13")
    stack.append("A=M")
    stack.append("M=D\n")

    return "\n".join(stack)

def write_binary_arithmetic(op: str) -> str:
    stack = []

    # pop y
    stack.append("@SP")
    stack.append("M=M-1")
    stack.append("A=M")
    stack.append("D=M")

    # pop x
    stack.append("@SP")
    stack.append("M=M-1")
    stack.append("A=M")
    
    # compute x op y
    if op == "add":
        stack.append("D=D+M")
    elif op == "sub":
        stack.append("D=M-D")
    elif op == "and":
        stack.append("D=D&M")
    else:
        stack.append("D=D|M")

    # push to stack
    stack.append("@SP")
    stack.append("A=M")
    stack.append("M=D")
    stack.append("@SP")
    stack.append("M=M+1\n")

    return "\n".join(stack)

def write_unary_arithmetic(op: str) -> str:
    stack = []

    # pop y
    stack.append("@SP")
    stack.append("M=M-1")
    stack.append("A=M")

    # compute op y
    if op == "neg":
        stack.append("M=-M")
    else:
        stack.append("M=!M")

    # push
    stack.append("@SP")
    stack.append("M=M+1\n")

    return "\n".join(stack)

JUMP_OP = {
    "eq": "JEQ",
    "gt": "JGT",
    "lt": "JLT"
}

def write_comparison(op: str, i: int) -> str:
    stack = []

    # pop y
    stack.append("@SP")
    stack.append("M=M-1")
    stack.append("A=M")
    stack.append("D=M")

    # pop x
    stack.append("@SP")
    stack.append("M=M-1")
    stack.append("A=M")
    stack.append("D=M-D")

    # compare
    stack.append(f"@IFTRUE{i}")
    stack.append(f"D;{JUMP_OP[op]}")

    # if not true
    stack.append("D=0")
    stack.append(f"@ENDIF{i}")
    stack.append("0;JMP")

    # if true
    stack.append(f"(IFTRUE{i})")
    stack.append("D=-1")

    # end if
    stack.append(f"(ENDIF{i})")

    # push
    stack.append("@SP")
    stack.append("A=M")
    stack.append("M=D")
    stack.append("@SP")
    stack.append("M=M+1\n")

    return "\n".join(stack)

def write_end() -> str:
    return """\
(END)
@END
0;JMP
"""
