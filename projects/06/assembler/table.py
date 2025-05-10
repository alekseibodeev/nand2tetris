def init_table() -> dict[str, int]:
    """Create dictionary and populate it with predefined symbols"""
    table = dict([(f"R{i}", i) for i in range(16)])
    table["SP"] = 0
    table["LCL"] = 1
    table["ARG"] = 2
    table["THIS"] = 3
    table["THAT"] = 4
    table["SCREEN"] = 16384
    table["KBD"] = 24576
    return table
