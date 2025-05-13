from typing import Self

class Table:
    def __init__(self: Self) -> None:
        self._table = Table._create_table()
        self._address = 16

    def add_entry(self: Self, symbol: str, value: int | None = None) -> None:
        if value == None:
            value = self._address
            self._address += 1
        self._table[symbol] = value

    def contains(self: Self, symbol: str) -> bool:
        return symbol in self._table

    def get_address(self: Self, symbol: str) -> int:
        return self._table[symbol]

    @staticmethod
    def _create_table() -> dict[str, int]:
        table = dict([(f"R{i}", i) for i in range(16)])
        table["SP"] = 0
        table["LCL"] = 1
        table["ARG"] = 2
        table["THIS"] = 3
        table["THAT"] = 4
        table["SCREEN"] = 16384
        table["KBD"] = 24576
        return table
