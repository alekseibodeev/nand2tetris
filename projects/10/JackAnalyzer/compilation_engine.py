from typing import Self
from pathlib import Path
from jack_tokenizer import JackTokenizer

class CompilationEngine:
    def __init__(self: Self, input_path: Path, output_path: Path):
        self._tokenizer = JackTokenizer(input_path)
        self._output_stream = open(output_path, "w")

    def compile(self: Self) -> None:
        self._tokenizer.advance()
        self._compile_class()
        self._output_stream.close()

    def _compile_class(self: Self) -> None:
        VARDEC = {"static", "field"}
        SUBROUTINE = {"constructor", "method", "function"}
        tokenizer = self._tokenizer

        self._write_line("<class>")
        self._process() # class keyword
        self._process() # class name
        self._process() # {

        while tokenizer.token_type() == "KEYWORD" and tokenizer.keyword() in VARDEC:
            self._compile_class_var_dec()

        while tokenizer.token_type() == "KEYWORD" and tokenizer.keyword() in SUBROUTINE:
            self._compile_subroutine_dec()

        self._process() # }
        self._write_line("</class>")

    def _compile_class_var_dec(self: Self) -> None:
        tokenizer = self._tokenizer

        self._write_line("<classVarDec>")
        self._process() # static | field keyword
        self._process() # type
        self._process() # var_name

        while tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == ",":
            self._process() # ,
            self._process() # var_name

        self._process() # ;
        self._write_line("</classVarDec>")

    def _compile_subroutine_dec(self: Self) -> None:
        self._write_line("<subroutineDec>")
        self._process() # constructor | method | function keyword
        self._process() # void | type 
        self._process() # subroutine name
        self._process() # (
        self._compile_parameter_list()
        self._process() # )
        self._compile_subroutine_body()
        self._write_line("</subroutineDec>")

    def _compile_parameter_list(self: Self) -> None:
        tokenizer = self._tokenizer

        self._write_line("<parameterList>")

        if tokenizer.token_type() == "KEYWORD":
            self._process() # type
            self._process() # var name

        while tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == ",":
            self._process() # ,
            self._process() # type
            self._process() # var name

        self._write_line("</parameterList>")

    def _compile_subroutine_body(self: Self) -> None:
        tokenizer = self._tokenizer

        self._write_line("<subroutineBody>")
        self._process() # {

        while tokenizer.token_type() == "KEYWORD" and tokenizer.keyword() == "var":
            self._compile_var_dec()

        self._compile_statements()
        self._process() # }
        self._write_line("</subroutineBody>")

    def _compile_var_dec(self: Self) -> None:
        tokenizer = self._tokenizer

        self._write_line("<varDec>")
        self._process() # var
        self._process() # type
        self._process() # var name

        while tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == ",":
            self._process() # ,
            self._process() # var name

        self._process() # ;
        self._write_line("</varDec>")

    def _compile_statements(self: Self) -> None:
        STATEMENT = {"let", "if", "while", "do", "return"}
        tokenizer = self._tokenizer

        self._write_line("<statements>")

        while tokenizer.token_type() == "KEYWORD" and tokenizer.keyword() in STATEMENT:
            keyword = tokenizer.keyword()

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

        self._write_line("</statements>")

    def _compile_let(self: Self) -> None:
        tokenizer = self._tokenizer

        self._write_line("<letStatement>")
        self._process() # let
        self._process() # var name

        if tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == "[":
            self._process() # [
            self._compile_expression()
            self._process() # ]

        self._process() # =
        self._compile_expression()
        self._process() # ;
        self._write_line("</letStatement>")

    def _compile_if(self: Self) -> None:
        tokenizer = self._tokenizer

        self._write_line("<ifStatement>")
        self._process() # if
        self._process() # (
        self._compile_expression()
        self._process() # )
        self._process() # {
        self._compile_statements()
        self._process() # }

        if tokenizer.token_type() == "KEYWORD" and tokenizer.keyword() == "else":
            self._process() # else
            self._process() # {
            self._compile_statements()
            self._process() # }

        self._write_line("</ifStatement>")

    def _compile_while(self: Self) -> None:
        self._write_line("<whileStatement>")
        self._process() # while
        self._process() # (
        self._compile_expression()
        self._process() # )
        self._process() # {
        self._compile_statements()
        self._process() # }
        self._write_line("</whileStatement>")

    def _compile_do(self: Self) -> None:
        tokenizer = self._tokenizer

        self._write_line("<doStatement>")
        self._process() # do
        self._process() # subroutine name

        if tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == ".":
            self._process() # .
            self._process() # subroutin name

        self._process() # (
        self._compile_expression_list()
        self._process() # )

        self._process() # ;
        self._write_line("</doStatement>")

    def _compile_return(self: Self) -> None:
        tokenizer = self._tokenizer

        self._write_line("<returnStatement>")
        self._process() # return

        if tokenizer.token_type() != "SYMBOL":
            self._compile_expression()

        self._process() # ;
        self._write_line("</returnStatement>")

    def _compile_expression(self: Self) -> None:
        OP = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
        tokenizer = self._tokenizer

        self._write_line("<expression>")
        self._compile_term()

        while tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() in OP:
            self._process() # op
            self._compile_term()

        self._write_line("</expression>")

    def _compile_term(self: Self) -> None:
        UNARY = {"-", "~"}
        tokenizer = self._tokenizer

        self._write_line("<term>")
        if tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == "(":
            self._process() # (
            self._compile_expression()
            self._process() # )
        elif tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() in UNARY:
            self._process() # - | ~
            self._compile_term()
        else:
            self._process() # constant, structure or procedure
        
        if tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == "[":
            self._process() # [
            self._compile_expression()
            self._process() # ]
        elif tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == ".":
            self._process() # .
            self._process() # subroutine name
        if tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == "(":
            self._process() # (
            self._compile_expression_list()
            self._process() # )

        self._write_line("</term>")

    def _compile_expression_list(self: Self) -> int:
        tokenizer = self._tokenizer
        count = 0

        self._write_line("<expressionList>")

        if tokenizer.token_type() != "SYMBOL" or tokenizer.symbol() != ")":
            self._compile_expression()
            count += 1

        while tokenizer.token_type() == "SYMBOL" and tokenizer.symbol() == ",":
            self._process() # ,
            self._compile_expression()
            count += 1

        self._write_line("</expressionList>")
        return count

    def _process(self: Self) -> None:
        SPECIALS = {"<": "&lt;", ">": "&gt;", "\"": "&quot;", "&": "&amp;"}
        tokenizer = self._tokenizer
        kind = tokenizer.token_type()
        tag = None
        val = None

        if kind == "KEYWORD":
            tag = kind.lower()
            val = tokenizer.keyword()
        elif kind == "SYMBOL":
            tag = kind.lower()
            val = tokenizer.symbol()
            val = SPECIALS.get(val, val)
        elif kind == "IDENTIFIER":
            tag = kind.lower()
            val = tokenizer.identifier()
        elif kind == "INT_CONST":
            tag = "integerConstant"
            val = tokenizer.int_val()
        elif kind == "STRING_CONST":
            tag = "stringConstant"
            val = tokenizer.string_val()

        self._write_line(f"<{tag}>{val}</{tag}>")
        tokenizer.advance()

    def _write_line(self: Self, text: str) -> None:
        self._output_stream.write(text + "\n")
