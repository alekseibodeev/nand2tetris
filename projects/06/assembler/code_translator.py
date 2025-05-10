def dest_to_bin(dest: str | None) -> str:
    """Translate symbolic dest to binary.

    >>> dest_to_bin(None)
    '000'

    >>> dest_to_bin('M')
    '001'

    >>> dest_to_bin('ADM')
    '111'
    """
    if not dest:
        return '000'
    m = 1 if 'M' in dest else 0
    d = 1 if 'D' in dest else 0
    a = 1 if 'A' in dest else 0
    return f"{a}{d}{m}"

COMP_COMMANDS = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}

def comp_to_bin(comp: str) -> str:
    """Translate symbolic comp to binary.

    >>> comp_to_bin('M-1')
    '1110010'

    >>> comp_to_bin('A-1')
    '0110010'

    >>> comp_to_bin('1')
    '0111111'
    """
    return COMP_COMMANDS[comp]

JUMP_COMMANDS = {
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}

def jump_to_bin(jump: str | None) -> str:
    """Translate symbolic jump to binary.

    >>> jump_to_bin(None)
    '000'

    >>> jump_to_bin('JMP')
    '111'

    >>> jump_to_bin('JEQ')
    '010'
    """
    if not jump:
        return "000"
    return JUMP_COMMANDS[jump]

def address_to_bin(address: int) -> str:
    """Translate decimal address to 16-bit long binary.

    Assume address will always be less than 2^15

    >>> address_to_bin(16)
    '0000000000010000'

    >>> address_to_bin(32767)
    '0111111111111111'
    """
    return f"{address:016b}"

if __name__ == "__main__":
    from doctest import run_docstring_examples
    
    def run_doctests(func):
        run_docstring_examples(func, globals(), name=func.__name__)

    run_doctests(dest_to_bin)
    run_doctests(comp_to_bin)
    run_doctests(jump_to_bin)
    run_doctests(address_to_bin)
