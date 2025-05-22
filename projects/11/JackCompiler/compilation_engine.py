from typing import Self
from pathlib import Path
from jack_tokenizer import JackTokenizer
from symbol_table import SymbolTable
from vmwriter import VMWriter

class CompilationEngine:
    _SEGMENTS = {
        "static": "static",
        "field": "this",
        "var": "local",
        "arg": "argument"
    }

    def __init__(self: Self, input_path: Path, output_path: Path):
        self._token = JackTokenizer(input_path)
        self._writer = VMWriter(output_path)
        self._class_table = SymbolTable()
        self._function_table = SymbolTable()
        self._class_name = ""
        self._label_count = 0

    def compile(self: Self) -> None:
        self._token.next()
        self._compile_class()
        self._writer.close()

    def _compile_class(self: Self) -> None:
        ### 'class' className '{' classVarDec* subroutineDec* '}'
        ###    1        2      3       4             5         6

        vardecs = {"static", "field"}
        subroutines = {"constructor", "method", "function"}

        self._token.next()                     # 1 class

        self._class_name = self._token.identifier()
        self._token.next()                     # 2 className
        self._token.next()                     # 3 {

        while self._token.is_keyword() and self._token.keyword() in vardecs:
            self._compile_class_var_dec()      # 4 classVarDec

        while self._token.is_keyword() and self._token.keyword() in subroutines:
            self._compile_subroutine_dec()     # 5 subroutineDec

        self._token.next()                     # 6 }

    def _compile_class_var_dec(self: Self) -> None:
        ### ('static'|'field') type varName (',' varName)* ';'
        ###          1          2      3      4     5       6

        vkind = self._token.keyword()
        self._token.next()                    # 1 ('static'|'field')

        vtype = self._token.keyword()
        self._token.next()                    # 2 type

        vname = self._token.identifier()
        self._token.next()                    # 3 varName

        self._class_table.define(vname, vtype, vkind)

        while self._token.is_symbol() and self._token.symbol() == ",":
            self._token.next()                # 4 ,

            vname = self._token.identifier()
            self._token.next()                # 5 varName

            self._class_table.define(vname, vtype, vkind)

        self._token.next()                   # 6 ;

    def _compile_constructor_dec(self: Self, fname: str) -> None:
        self._compile_procedure_dec(fname)
        n = self._class_table.var_count("field")
        self._writer.write_push("constant", n)
        self._writer.write_call("Memory.alloc", 1)
        self._writer.write_pop("pointer", 0)

    def _compile_method_dec(self: Self, fname: str) -> None:
        self._compile_procedure_dec(fname)
        self._writer.write_push("argument", 0)
        self._writer.write_pop("pointer", 0)

    def _compile_procedure_dec(self: Self, fname: str) -> None:
        n = self._function_table.var_count("var")
        self._writer.write_function(f"{self._class_name}.{fname}", n)

    def _compile_subroutine_dec(self: Self) -> None:
        ### ('constructor'|'function'|'method') type subroutinName
        ###                     1                2         3
        ### '(' parameterList ')' subroutineBody
        ###  4        5        6        7

        self._function_table.reset()

        ftype = self._token.keyword()
        self._token.next()              # 1 ('constructor'|'function'|'method')

        if ftype == "method":
            self._function_table.define("this", self._class_name, "arg")

        self._token.next()              # 2 type

        fname = self._token.identifier()
        self._token.next()              # 3 subroutinName
        self._token.next()              # 4 (
        self._compile_parameter_list()  # 5 parameterList
        self._token.next()              # 6 )
        self._compile_subroutine_body(ftype, fname) # 7 subroutineBody

    def _compile_parameter_list(self: Self) -> None:
        ### ((type varName) (',' type varName)*)?
        ###    1      2       3   4      5

        if self._token.is_symbol() and self._token.symbol() == ")":
            return

        vkind = "arg"

        vtype = self._token.keyword()
        self._token.next()                   # 1 type

        vname = self._token.identifier()
        self._token.next()                   # 2 varName

        self._function_table.define(vname, vtype, vkind)

        while self._token.is_symbol() and self._token.symbol() == ",":
            self._token.next()               # 3 ,

            vtype = self._token.keyword()
            self._token.next()               # 4 type

            vname = self._token.identifier()
            self._token.next()               # 5 varName

            self._function_table.define(vname, vtype, vkind)

    def _compile_subroutine_body(self: Self, ftype: str, fname: str) -> None:
        ### '{' varDec* statements '}'
        ###  1     2         3      4

        self._token.next()                   # 1 {

        while self._token.is_keyword() and self._token.keyword() == "var":
            self._compile_var_dec()          # 2 varDec

        if ftype == "constructor":
            self._compile_constructor_dec(fname)
        elif ftype == "method":
            self._compile_method_dec(fname)
        else:
            self._compile_procedure_dec(fname)

        self._compile_statements()           # 3 statements
        self._token.next()                   # 4 }

    def _compile_var_dec(self: Self) -> None:
        ### 'var' type varName (',' varName)* ';'
        ###   1    2      3      4     5       6

        vkind = self._token.keyword()
        self._token.next()                   # 1 var

        vtype = self._token.keyword()
        self._token.next()                   # 2 type

        vname = self._token.identifier()
        self._token.next()                   # 3 varName

        self._function_table.define(vname, vtype, vkind)

        while self._token.is_symbol() and self._token.symbol() == ",":
            self._token.next()               # 4 ,

            vname = self._token.identifier()
            self._token.next()               # 5 varName

            self._function_table.define(vname, vtype, vkind)

        self._token.next()                   # 6 ;

    def _compile_statements(self: Self) -> None:
        statements = {"let", "if", "while", "do", "return"}

        while self._token.is_keyword() and self._token.keyword() in statements:
            keyword = self._token.keyword()

            if keyword == "let":
                self._compile_let()
            elif keyword == "if":
                self._compile_if()
            elif keyword == "while":
                self._compile_while()
            elif keyword == "do":
                self._compile_do()
            elif keyword == "return":
                self._compile_return()

    def _compile_array_assignement(self: Self) -> None:
        ### varName '[' expression1 ']' '=' expression2
        ###    1     2       3       4   5       6

        vname = self._token.identifier()
        self._token.next()                   # 1 varName
        
        if self._function_table.contains(vname):
            vkind = self._function_table.kind_of(vname)
            index = self._function_table.index_of(vname)
        else:
            vkind = self._class_table.kind_of(vname)
            index = self._class_table.index_of(vname)

        segment = self._SEGMENTS[vkind]
        self._writer.write_push(segment, index)

        self._token.next()                   # 2 [
        self._compile_expression()           # 3 expression1
        self._token.next()                   # 3 ]

        self._writer.write_arithmetic("add")

        self._token.next()                   # 4 = 
        self._compile_expression()           # 5 expression2

        self._writer.write_pop("temp", 0)
        self._writer.write_pop("pointer", 1)
        self._writer.write_push("temp", 0)
        self._writer.write_pop("that", 0)

    def _compile_assignement(self: Self) -> None:
        ### varName '=' expression
        ###    1     2      3

        vname = self._token.identifier()
        self._token.next()                   # 1 varName

        if self._function_table.contains(vname):
            vkind = self._function_table.kind_of(vname)
            index = self._function_table.index_of(vname)
        else:
            vkind = self._class_table.kind_of(vname)
            index = self._class_table.index_of(vname)

        segment = self._SEGMENTS[vkind]

        self._token.next()                   # 2 =
        self._compile_expression()           # 3 expression

        self._writer.write_pop(segment, index)

    def _compile_let(self: Self) -> None:
        ### 'let' assignemnt ';'
        ###   1        2      3

        self._token.next()                   # 1 let

        if self._is_array_access():          # 2 assignement
            self._compile_array_assignement()
        else:
            self._compile_assignement()

        self._token.next()                   # 3 ;

    def _compile_if(self: Self) -> None:
        ### 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        ###  1    2      3       4   5      6       7      8    9      10     11

        label1 = self._get_label()

        self._token.next()                   # 1 if
        self._token.next()                   # 2 (
        self._compile_expression()           # 3 expression

        self._writer.write_arithmetic("not")
        self._writer.write_if(label1)

        self._token.next()                   # 4 )
        self._token.next()                   # 5 {
        self._compile_statements()           # 6 statements
        self._token.next()                   # 7 }

        if self._token.is_keyword() and self._token.keyword() == "else":
            label2 = self._get_label()

            self._writer.write_goto(label2)
            self._writer.write_label(label1)

            self._token.next()               # 8 else
            self._token.next()               # 9 {
            self._compile_statements()       # 10 statments
            self._token.next()               # 11 }

            self._writer.write_label(label2)
        else:
            self._writer.write_label(label1)

    def _compile_while(self: Self) -> None:
        ### 'while' '(' expression ')' '{' statements '}'
        ###    1     2       3      4   5       6      7

        label1 = self._get_label()
        label2 = self._get_label()

        self._token.next()                   # 1 while
        self._token.next()                   # 2 (

        self._writer.write_label(label1)

        self._compile_expression()           # 3 expression

        self._writer.write_arithmetic("not")
        self._writer.write_if(label2)

        self._token.next()                   # 4 )
        self._token.next()                   # 5 {
        self._compile_statements()           # 6 statements

        self._writer.write_goto(label1)
        self._writer.write_label(label2)

        self._token.next()                   # 7 }

    def _compile_do(self: Self) -> None:
        ### 'do' expression ';'
        ###  1        2      3

        self._token.next()                   # 1 do
        self._compile_expression()           # 2 expression

        self._writer.write_pop("temp" , 0)

        self._token.next()                   # 3 ;

    def _compile_return(self: Self) -> None:
        ### 'return' expression? ';'
        ###    1          2       3

        self._token.next()                   # 1 return

        if not self._token.is_symbol():
            self._compile_expression()       # 2 expression
        else:
            self._writer.write_push("constant", 0)

        self._writer.write_return()

        self._token.next()                   # 3 ;

    def _compile_expression(self: Self) -> None:
        ### term (op term)*
        ###  1    2   3

        operators = {
            "+": "add", "-": "sub", "*": "Math.multiply", "/": "Math.divide",
            "&": "and", "|": "or", "<": "lt", ">": "gt", "=": "eq"
        }

        self._compile_term()                 # 1 term

        while self._token.is_symbol() and self._token.symbol() in operators:
            operator = self._token.symbol()

            self._token.next()               # 2 op
            self._compile_term()             # 3 term

            if operator in {'*', '/'}:
                self._writer.write_call(operators[operator], 2)
            else:
                self._writer.write_arithmetic(operators[operator])

    def _is_parenthesised_expression(self: Self) -> bool:
        return self._token.is_symbol() and self._token.symbol() == "("

    def _compile_parenthesised_expression(self: Self) -> None:
        ### '(' expression ')'
        ###  1       2      3
        self._token.next()                   # 1 (
        self._compile_expression()           # 2 expression
        self._token.next()                   # 3 )

    def _is_unary_operator_expression(self: Self) -> bool:
        return self._token.is_symbol() and self._token.symbol() in {"-", "~"}

    def _compile_unary_operator_expression(self: Self) -> None:
        ### op term
        ### 1   2

        operators = {"-": "neg", "~": "not"}
        operator = self._token.symbol()

        self._token.next()                   # 1 op
        self._compile_term()                 # 2 term

        self._writer.write_arithmetic(operators[operator])

    def _compile_int_const(self: Self) -> None:
        self._writer.write_push("constant", self._token.int_val())
        self._token.next()

    def _compile_string_const(self: Self) -> None:
        string = self._token.string_val()
        n = len(string)
        self._writer.write_push("constant", n)
        self._writer.write_call("String.new", 1)

        for c in string:
            self._writer.write_push("constant", ord(c))
            self._writer.write_call("String.appendChar", 2) # methods have implicit argument this

        self._token.next()

    def _is_keyword_const(self: Self) -> bool:
        keywords = {"null", "false", "true", "this"}
        return self._token.is_keyword() and self._token.keyword() in keywords

    def _compile_keyword_const(self: Self) -> None:
        keyword = self._token.keyword()
        if keyword == "true":
            self._writer.write_push("constant", 1)
            self._writer.write_arithmetic("neg")
        elif keyword == "this":
            self._writer.write_push("pointer", 0)
        else:
            self._writer.write_push("constant", 0)

        self._token.next()

    def _is_this_method_call(self: Self) -> bool:
        self._token.next()
        is_invokation = self._token.is_symbol() and self._token.symbol() == "("
        self._token.previous()
        return is_invokation

    def _compile_this_method_call(self: Self) -> None:
        ### subroutineName '(' expressionList ')'
        ###       1         2         3        4

        self._writer.write_push("pointer", 0) # push this
        fname = self._token.identifier()

        self._token.next()                   # 1 subroutineName
        self._token.next()                   # 2 (
        n = self._compile_expression_list()  # 3 expressionList
        self._token.next()                   # 4 )

        self._writer.write_call(f"{self._class_name}.{fname}", n + 1)

    def _is_class_function_call(self: Self) -> bool:
        vname = self._token.identifier()
        self._token.next()
        is_dot_notation = self._token.is_symbol() and self._token.symbol() == "."
        self._token.previous()
        return (
            is_dot_notation
            and not self._function_table.contains(vname)
            and not self._class_table.contains(vname)
        )

    def _compile_class_function_call(self: Self) -> None:
        ### className '.' subroutineName '(' expressionList ')'
        ###     1      2         3        4         5        6

        cname = self._token.identifier()
        self._token.next()                   # 1 className
        self._token.next()                   # 2 .

        fname = self._token.identifier()
        self._token.next()                   # 3 subroutineName
        self._token.next()                   # 4 (
        n = self._compile_expression_list()  # 5 expressionList
        self._token.next()                   # 6 )

        self._writer.write_call(f"{cname}.{fname}", n)

    def _is_method_call(self: Self) -> bool:
        vname = self._token.identifier()
        self._token.next()
        is_dot_notation = self._token.is_symbol() and self._token.symbol() == "."
        self._token.previous()
        return (
            is_dot_notation and
            (self._function_table.contains(vname) or
             self._class_table.contains(vname))
        )

    def _compile_method_call(self: Self) -> None:
        ### varName '.' subroutinName '(' expressionList ')'
        ###    1     2        3        4         5        6

        vname = self._token.identifier()
        self._token.next()                   # 1 varName
        self._token.next()                   # 2 .

        if self._function_table.contains(vname):
            cname = self._function_table.type_of(vname)
            vkind = self._function_table.kind_of(vname)
            index = self._function_table.index_of(vname)
        else:
            cname = self._class_table.type_of(vname)
            vkind = self._class_table.kind_of(vname)
            index = self._class_table.index_of(vname)

        segment = self._SEGMENTS[vkind]
        self._writer.write_push(segment, index)

        fname = self._token.identifier()
        self._token.next()                   # 3 subroutinName
        self._token.next()                   # 4 (
        n = self._compile_expression_list()  # 5 expressionList
        self._token.next()                   # 6 )

        self._writer.write_call(f"{cname}.{fname}", n + 1)

    def _compile_var_name(self: Self) -> None:
        vname = self._token.identifier()

        if self._function_table.contains(vname):
            vkind = self._function_table.kind_of(vname)
            index = self._function_table.index_of(vname)
        else:
            vkind = self._class_table.kind_of(vname)
            index = self._class_table.index_of(vname)

        segment = self._SEGMENTS[vkind]
        self._writer.write_push(segment, index)

        self._token.next()

    def _is_array_access(self: Self) -> bool:
        self._token.next()
        symbol = self._token.symbol()
        self._token.previous()
        return symbol == "["

    def _compile_array_access(self: Self) -> None:
        ### varName '[' expression ']'
        ###    1     2      3       4

        vname = self._token.identifier()
        self._token.next()                   # 1 varName
        
        if self._function_table.contains(vname):
            vkind = self._function_table.kind_of(vname)
            index = self._function_table.index_of(vname)
        else:
            vkind = self._class_table.kind_of(vname)
            index = self._class_table.index_of(vname)

        segment = self._SEGMENTS[vkind]
        self._writer.write_push(segment, index)

        self._token.next()                   # 2 [
        self._compile_expression()           # 3 expression
        self._token.next()                   # 4 ]
        
        self._writer.write_arithmetic("add")
        self._writer.write_pop("pointer", 1)
        self._writer.write_push("that", 0)

    def _compile_term(self: Self) -> None:
        if self._is_parenthesised_expression():
            self._compile_parenthesised_expression()
        elif self._is_unary_operator_expression():
            self._compile_unary_operator_expression()
        elif self._token.is_int():
            self._compile_int_const()
        elif self._token.is_string():
            self._compile_string_const()
        elif self._is_keyword_const():
            self._compile_keyword_const()
        elif self._is_array_access():
            self._compile_array_access()
        elif self._is_this_method_call():
            self._compile_this_method_call()
        elif self._is_method_call():
            self._compile_method_call()
        elif self._is_class_function_call():
            self._compile_class_function_call()
        else:
            self._compile_var_name()

    def _compile_expression_list(self: Self) -> int:
        ### (expression (',' expression)*)?
        ###      1        2       3

        if self._token.is_symbol() and self._token.symbol() == ")":
            return 0

        self._compile_expression()           # 1 expression
        count = 1

        while self._token.is_symbol() and self._token.symbol() == ",":
            self._token.next()               # 2 ,
            self._compile_expression()       # 3 expression
            count += 1

        return count

    def _get_label(self: Self) -> str:
        label = f"L{self._label_count}"
        self._label_count += 1
        return label
