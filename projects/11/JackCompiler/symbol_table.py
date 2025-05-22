from typing import Self

class SymbolTable:
    def __init__(self: Self) -> None:
        self._table = {} # (type, kind, index)
        self._count = {"static": 0, "field": 0, "arg": 0, "var": 0}

    def contains(self: Self, vname: str) -> bool:
        return vname in self._table

    def reset(self: Self) -> None:
        self._table.clear()
        self._count = {"static": 0, "field": 0, "arg": 0, "var": 0}

    def define(self: Self, vname: str, vtype: str, vkind: str) -> None:
        self._table[vname] = (vtype, vkind, self._count[vkind])
        self._count[vkind] += 1

    def var_count(self: Self, vkind: str) -> int:
        return self._count[vkind]

    def type_of(self: Self, vname: str) -> str:
        return self._table[vname][0]

    def kind_of(self: Self, vname: str) -> str:
        return self._table[vname][1]

    def index_of(self: Self, vname: str) -> int:
        return self._table[vname][2]
