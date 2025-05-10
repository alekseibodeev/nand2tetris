def is_comment(line: str) -> bool:
    """Check wheather the given line is a comment.

    Assume the line is already trimmed

    >>> is_comment('// I am a comment!')
    True

    >>> is_comment('Not a comment')
    False
    """
    return line.startswith("//")

def is_address(line: str) -> bool:
    """Check wheather the given line is an A Instruction.

    Assume the line is already trimmed

    >>> is_address('@hello')
    True

    >>> is_address('(LOOP)')
    False

    >>> is_address('M=D')
    False
    """
    return line.startswith('@')

def is_label(line: str) -> bool:
    """Check wheather the given line is a C Instruction.

    Assume the line is already trimmed

    >>> is_label('@hello')
    False

    >>> is_label('(LOOP)')
    True

    >>> is_label('M=D')
    False
    """
    return line.startswith('(') and line.endswith(')')

def get_symbol_from_address(line: str) -> str:
    """Extract symbol from an A Instruction.

    Assume the line is valid A Instruction

    >>> get_symbol_from_address('@hello')
    'hello'
    """
    return line[1:]

def get_symbol_from_label(line: str) -> str:
    """Extract symbol from an L Instruction.

    Assume the line is valid L Instruction

    >>> get_symbol_from_label('(LOOP)')
    'LOOP'
    """
    return line[1:-1]

def get_dest(line: str) -> str | None:
    """Extract dest from a C Instruction.

    Assume the line is a valid C Instruction

    >>> get_dest('M=M+1')
    'M'

    >>> get_dest('D;JMP') is None
    True
    """
    i = line.find('=')
    return line[:i] if i >= 0 else None

def get_comp(line: str) -> str:
    """Extract dest from a C Instruction.

    Assume the line is a valid C Instruction

    >>> get_comp('M=M+1')
    'M+1'

    >>> get_comp('D;JMP')
    'D'
    """
    i = find_c_instruction_pivot(line)
    return line[i+1:] if line[i] == "=" else line[:i]

def get_jump(line: str) -> str | None:
    """Extract jump from a C Instruction.

    Assume the line is valid C Instruction

    >>> get_jump('M=M+1') is None
    True

    >>> get_jump('D;JGE')
    'JGE'
    """
    i = line.find(";")
    return line[i+1:] if i >= 0 else None

def find_c_instruction_pivot(line: str) -> int:
    """Find index of divider that splits C Instructions.

    ; - splits jump instructions
    = - splits computations
    """
    for i, c in enumerate(line):
        if c == "=" or c == ";":
            return i
    return -1

def remove_spaces(line: str) -> str:
    """Remove all space from the given line

    >>> remove_spaces('Hello, World')
    'Hello,World'

    >>> remove_spaces('Hello')
    'Hello'
    """
    return line.replace(" ", "")

if __name__ == "__main__":
    from doctest import run_docstring_examples
    
    def run_doctests(func):
        run_docstring_examples(func, globals(), name=func.__name__)

    run_doctests(is_comment)
    run_doctests(is_address)
    run_doctests(is_label)
    run_doctests(get_symbol_from_address)
    run_doctests(get_symbol_from_label)
    run_doctests(get_dest)
    run_doctests(get_comp)
    run_doctests(get_jump)
    run_doctests(remove_spaces)
