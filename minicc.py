#!/usr/bin/env python3
import sys
import json
import argparse
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, Tuple


class TokenType(Enum):
    INT_KW = auto()
    FLOAT_KW = auto()
    BOOL_KW = auto()
    STRING_KW = auto()
    VOID_KW = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    PRINT = auto()
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    ASSIGN = auto()
    EQ = auto()
    NEQ = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    EOF = auto()
    UNKNOWN = auto()


KEYWORDS = {
    'int': TokenType.INT_KW,
    'float': TokenType.FLOAT_KW,
    'bool': TokenType.BOOL_KW,
    'string': TokenType.STRING_KW,
    'void': TokenType.VOID_KW,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'return': TokenType.RETURN,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'print': TokenType.PRINT,
}

KEYWORD_NAMES = {v: k for k, v in KEYWORDS.items()}

TOKEN_DISPLAY = {
    TokenType.INT_KW: 'KW_INT', TokenType.FLOAT_KW: 'KW_FLOAT',
    TokenType.BOOL_KW: 'KW_BOOL', TokenType.STRING_KW: 'KW_STRING',
    TokenType.VOID_KW: 'KW_VOID', TokenType.IF: 'KW_IF',
    TokenType.ELSE: 'KW_ELSE', TokenType.WHILE: 'KW_WHILE',
    TokenType.FOR: 'KW_FOR', TokenType.RETURN: 'KW_RETURN',
    TokenType.TRUE: 'KW_TRUE', TokenType.FALSE: 'KW_FALSE',
    TokenType.PRINT: 'KW_PRINT', TokenType.IDENTIFIER: 'IDENT',
    TokenType.INT_LITERAL: 'INT_LIT', TokenType.FLOAT_LITERAL: 'FLOAT_LIT',
    TokenType.STRING_LITERAL: 'STR_LIT', TokenType.PLUS: 'PLUS',
    TokenType.MINUS: 'MINUS', TokenType.STAR: 'STAR',
    TokenType.SLASH: 'SLASH', TokenType.PERCENT: 'PERCENT',
    TokenType.ASSIGN: 'ASSIGN', TokenType.EQ: 'EQ',
    TokenType.NEQ: 'NEQ', TokenType.LT: 'LT',
    TokenType.GT: 'GT', TokenType.LE: 'LE',
    TokenType.GE: 'GE', TokenType.AND: 'AND',
    TokenType.OR: 'OR', TokenType.NOT: 'NOT',
    TokenType.LPAREN: 'LPAREN', TokenType.RPAREN: 'RPAREN',
    TokenType.LBRACE: 'LBRACE', TokenType.RBRACE: 'RBRACE',
    TokenType.LBRACKET: 'LBRACKET', TokenType.RBRACKET: 'RBRACKET',
    TokenType.SEMICOLON: 'SEMI', TokenType.COMMA: 'COMMA',
    TokenType.EOF: 'EOF', TokenType.UNKNOWN: 'UNKNOWN',
}


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    col: int

    def display_type(self):
        return TOKEN_DISPLAY.get(self.type, self.type.name)


@dataclass
class LexerError:
    message: str
    line: int
    col: int
    context: str


class Lexer:
    def __init__(self, source: str, filename: str = "<stdin>"):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []
        self.errors: List[LexerError] = []

    def _peek(self) -> str:
        if self.pos < len(self.source):
            return self.source[self.pos]
        return '\0'

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _match(self, expected: str) -> bool:
        if self.pos < len(self.source) and self.source[self.pos] == expected:
            self._advance()
            return True
        return False

    def _get_context(self, line: int) -> str:
        lines = self.source.split('\n')
        if 1 <= line <= len(lines):
            return lines[line - 1].rstrip()
        return ""

    def _skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self._peek()
            if ch in ' \t\r\n':
                self._advance()
            elif ch == '/' and self.pos + 1 < len(self.source):
                if self.source[self.pos + 1] == '/':
                    self._advance()
                    self._advance()
                    while self.pos < len(self.source) and self._peek() != '\n':
                        self._advance()
                elif self.source[self.pos + 1] == '*':
                    self._advance()
                    self._advance()
                    while self.pos < len(self.source):
                        if self._peek() == '*' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/':
                            self._advance()
                            self._advance()
                            break
                        self._advance()
                else:
                    break
            else:
                break

    def _read_string(self) -> Optional[str]:
        result = []
        while self.pos < len(self.source) and self._peek() != '"':
            ch = self._advance()
            if ch == '\\':
                if self.pos < len(self.source):
                    esc = self._advance()
                    escape_map = {'n': '\n', 't': '\t', '\\': '\\', '"': '"', '0': '\0'}
                    result.append(escape_map.get(esc, '\\' + esc))
            else:
                result.append(ch)
        if self.pos >= len(self.source):
            return None
        self._advance()
        return ''.join(result)

    def _read_number(self) -> Token:
        start_line, start_col = self.line, self.col
        num_str = ""
        is_float = False
        while self.pos < len(self.source) and (self._peek().isdigit() or self._peek() == '.'):
            if self._peek() == '.':
                if is_float:
                    break
                is_float = True
            num_str += self._advance()
        if num_str.endswith('.'):
            num_str += '0'
        if is_float:
            return Token(TokenType.FLOAT_LITERAL, float(num_str), start_line, start_col)
        return Token(TokenType.INT_LITERAL, int(num_str), start_line, start_col)

    def _read_identifier(self) -> str:
        result = []
        while self.pos < len(self.source) and (self._peek().isalnum() or self._peek() == '_'):
            result.append(self._advance())
        return ''.join(result)

    def tokenize(self) -> Tuple[List[Token], List[LexerError]]:
        while True:
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                self.tokens.append(Token(TokenType.EOF, None, self.line, self.col))
                break

            start_line, start_col = self.line, self.col
            ch = self._peek()

            if ch == '"':
                self._advance()
                val = self._read_string()
                if val is None:
                    self.errors.append(LexerError(
                        "Unterminated string literal", start_line, start_col,
                        self._get_context(start_line)))
                    self.tokens.append(Token(TokenType.STRING_LITERAL, "", start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.STRING_LITERAL, val, start_line, start_col))
            elif ch.isdigit():
                self.tokens.append(self._read_number())
            elif ch.isalpha() or ch == '_':
                ident = self._read_identifier()
                tt = KEYWORDS.get(ident, TokenType.IDENTIFIER)
                if tt == TokenType.TRUE:
                    self.tokens.append(Token(tt, True, start_line, start_col))
                elif tt == TokenType.FALSE:
                    self.tokens.append(Token(tt, False, start_line, start_col))
                else:
                    self.tokens.append(Token(tt, ident, start_line, start_col))
            elif ch == '+':
                self._advance()
                self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_col))
            elif ch == '-':
                self._advance()
                self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_col))
            elif ch == '*':
                self._advance()
                self.tokens.append(Token(TokenType.STAR, '*', start_line, start_col))
            elif ch == '/':
                self._advance()
                self.tokens.append(Token(TokenType.SLASH, '/', start_line, start_col))
            elif ch == '%':
                self._advance()
                self.tokens.append(Token(TokenType.PERCENT, '%', start_line, start_col))
            elif ch == '=':
                self._advance()
                if self._match('='):
                    self.tokens.append(Token(TokenType.EQ, '==', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_col))
            elif ch == '!':
                self._advance()
                if self._match('='):
                    self.tokens.append(Token(TokenType.NEQ, '!=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.NOT, '!', start_line, start_col))
            elif ch == '<':
                self._advance()
                if self._match('='):
                    self.tokens.append(Token(TokenType.LE, '<=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', start_line, start_col))
            elif ch == '>':
                self._advance()
                if self._match('='):
                    self.tokens.append(Token(TokenType.GE, '>=', start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', start_line, start_col))
            elif ch == '&':
                self._advance()
                if self._match('&'):
                    self.tokens.append(Token(TokenType.AND, '&&', start_line, start_col))
                else:
                    self.errors.append(LexerError(
                        f"Unexpected character '&'", start_line, start_col,
                        self._get_context(start_line)))
                    self.tokens.append(Token(TokenType.UNKNOWN, '&', start_line, start_col))
            elif ch == '|':
                self._advance()
                if self._match('|'):
                    self.tokens.append(Token(TokenType.OR, '||', start_line, start_col))
                else:
                    self.errors.append(LexerError(
                        f"Unexpected character '|'", start_line, start_col,
                        self._get_context(start_line)))
                    self.tokens.append(Token(TokenType.UNKNOWN, '|', start_line, start_col))
            elif ch == '(':
                self._advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_col))
            elif ch == ')':
                self._advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_col))
            elif ch == '{':
                self._advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_col))
            elif ch == '}':
                self._advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_col))
            elif ch == '[':
                self._advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
            elif ch == ']':
                self._advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_col))
            elif ch == ';':
                self._advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_col))
            elif ch == ',':
                self._advance()
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_col))
            else:
                self._advance()
                self.errors.append(LexerError(
                    f"Illegal character '{ch}'", start_line, start_col,
                    self._get_context(start_line)))
                self.tokens.append(Token(TokenType.UNKNOWN, ch, start_line, start_col))

        return self.tokens, self.errors


class ASTNodeType(Enum):
    PROGRAM = auto()
    VAR_DECL = auto()
    ARRAY_DECL = auto()
    FUNC_DEF = auto()
    PARAM = auto()
    BLOCK = auto()
    ASSIGN = auto()
    ARRAY_ASSIGN = auto()
    IF = auto()
    WHILE = auto()
    FOR = auto()
    RETURN = auto()
    PRINT = auto()
    BINARY_OP = auto()
    UNARY_OP = auto()
    CALL = auto()
    ARRAY_ACCESS = auto()
    INT_LIT = auto()
    FLOAT_LIT = auto()
    BOOL_LIT = auto()
    STRING_LIT = auto()
    IDENTIFIER = auto()


class IROp(Enum):
    ASSIGN = "assign"
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    EQ = "eq"
    NEQ = "neq"
    LT = "lt"
    GT = "gt"
    LE = "le"
    GE = "ge"
    AND = "and"
    OR = "or"
    NOT = "not"
    NEG = "neg"
    ARRAY_LOAD = "array_load"
    ARRAY_STORE = "array_store"
    CALL = "call"
    RETURN = "return"
    PRINT = "print"
    LABEL = "label"
    JUMP = "jump"
    JUMP_IF = "jump_if"
    JUMP_IF_NOT = "jump_if_not"
    PARAM = "param"


@dataclass
class IRInst:
    op: IROp
    result: Optional[str] = None
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    extra: Optional[Any] = None

    def to_dict(self) -> Dict:
        d = {"op": self.op.value}
        if self.result is not None:
            d["result"] = self.result
        if self.arg1 is not None:
            d["arg1"] = self.arg1
        if self.arg2 is not None:
            d["arg2"] = self.arg2
        if self.extra is not None:
            d["extra"] = self.extra
        return d

    def __str__(self) -> str:
        op = self.op.value
        if self.op == IROp.LABEL:
            return f"{self.arg1}:"
        elif self.op == IROp.JUMP:
            return f"  jump {self.arg1}"
        elif self.op == IROp.JUMP_IF:
            return f"  jump_if {self.arg1} {self.arg2}"
        elif self.op == IROp.JUMP_IF_NOT:
            return f"  jump_if_not {self.arg1} {self.arg2}"
        elif self.op == IROp.ASSIGN:
            return f"  {self.result} = {self.arg1}"
        elif self.op == IROp.ARRAY_LOAD:
            return f"  {self.result} = {self.arg1}[{self.arg2}]"
        elif self.op == IROp.ARRAY_STORE:
            return f"  {self.arg1}[{self.arg2}] = {self.result}"
        elif self.op in (IROp.ADD, IROp.SUB, IROp.MUL, IROp.DIV, IROp.MOD,
                         IROp.EQ, IROp.NEQ, IROp.LT, IROp.GT, IROp.LE, IROp.GE,
                         IROp.AND, IROp.OR):
            op_map = {IROp.ADD: '+', IROp.SUB: '-', IROp.MUL: '*', IROp.DIV: '/', IROp.MOD: '%',
                      IROp.EQ: '==', IROp.NEQ: '!=', IROp.LT: '<', IROp.GT: '>',
                      IROp.LE: '<=', IROp.GE: '>=', IROp.AND: '&&', IROp.OR: '||'}
            sym = op_map.get(self.op, op)
            return f"  {self.result} = {self.arg1} {sym} {self.arg2}"
        elif self.op in (IROp.NOT, IROp.NEG):
            sym = '!' if self.op == IROp.NOT else '-'
            return f"  {self.result} = {sym}{self.arg1}"
        elif self.op == IROp.CALL:
            args = self.extra if self.extra else []
            return f"  {self.result} = call {self.arg1}({', '.join(args)})"
        elif self.op == IROp.RETURN:
            if self.arg1:
                return f"  return {self.arg1}"
            return f"  return"
        elif self.op == IROp.PRINT:
            return f"  print {self.arg1}"
        elif self.op == IROp.PARAM:
            return f"  param {self.arg1}"
        return f"  {op} {self.result} {self.arg1} {self.arg2}"


@dataclass
class BasicBlock:
    id: int
    label: str
    instructions: List[IRInst] = field(default_factory=list)
    predecessors: List[int] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)
    jump_condition: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "label": self.label,
            "instructions": [inst.to_dict() for inst in self.instructions],
            "predecessors": self.predecessors,
            "successors": self.successors,
            "jump_condition": self.jump_condition,
        }


@dataclass
class FunctionIR:
    name: str
    instructions: List[IRInst] = field(default_factory=list)
    basic_blocks: List[BasicBlock] = field(default_factory=list)
    optimized_instructions: Optional[List[IRInst]] = None
    optimized_basic_blocks: Optional[List[BasicBlock]] = None

    def to_dict(self, optimized: bool = False, compare: bool = False) -> Dict:
        if compare and self.optimized_instructions is not None:
            return {
                "name": self.name,
                "before": {
                    "instructions": [inst.to_dict() for inst in self.instructions],
                    "basic_blocks": [bb.to_dict() for bb in self.basic_blocks],
                },
                "after": {
                    "instructions": [inst.to_dict() for inst in self.optimized_instructions],
                    "basic_blocks": [bb.to_dict() for bb in self.optimized_basic_blocks] if self.optimized_basic_blocks else [],
                },
                "diff": {
                    "instructions_before": len(self.instructions),
                    "instructions_after": len(self.optimized_instructions),
                    "instructions_removed": len(self.instructions) - len(self.optimized_instructions),
                    "blocks_before": len(self.basic_blocks),
                    "blocks_after": len(self.optimized_basic_blocks) if self.optimized_basic_blocks else 0,
                }
            }
        insts = self.optimized_instructions if (optimized and self.optimized_instructions is not None) else self.instructions
        blocks = self.optimized_basic_blocks if (optimized and self.optimized_basic_blocks is not None) else self.basic_blocks
        return {
            "name": self.name,
            "instructions": [inst.to_dict() for inst in insts],
            "basic_blocks": [bb.to_dict() for bb in blocks],
        }


@dataclass
class SourcePos:
    line: int
    col: int


@dataclass
class ASTNode:
    type: ASTNodeType
    children: List[Any] = field(default_factory=list)
    value: Any = None
    pos: Optional[SourcePos] = None
    inferred_type: Optional[str] = None

    def to_dict(self) -> Dict:
        d: Dict[str, Any] = {"node": self.type.name}
        if self.value is not None:
            d["value"] = self.value
        if self.pos:
            d["pos"] = {"line": self.pos.line, "col": self.pos.col}
        if self.inferred_type:
            d["inferred_type"] = self.inferred_type
        if self.children:
            if self.type == ASTNodeType.FUNC_DEF:
                params = [c for c in self.children if c.type == ASTNodeType.PARAM]
                body = self.children[-1] if self.children else None
                d["params"] = [p.to_dict() for p in params]
                if body and body.type == ASTNodeType.BLOCK:
                    d["body"] = body.to_dict()
            else:
                d["children"] = [c.to_dict() if isinstance(c, ASTNode) else c for c in self.children]
        return d


@dataclass
class ParseError:
    message: str
    line: int
    col: int


TYPE_TOKENS = {
    TokenType.INT_KW, TokenType.FLOAT_KW,
    TokenType.BOOL_KW, TokenType.STRING_KW, TokenType.VOID_KW,
}

TYPE_NAMES = {
    TokenType.INT_KW: 'int',
    TokenType.FLOAT_KW: 'float',
    TokenType.BOOL_KW: 'bool',
    TokenType.STRING_KW: 'string',
    TokenType.VOID_KW: 'void',
}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[ParseError] = []

    def _cur(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _peek(self, offset: int = 0) -> Token:
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def _advance(self) -> Token:
        tok = self._cur()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _match(self, *types: TokenType) -> Optional[Token]:
        if self._cur().type in types:
            return self._advance()
        return None

    def _expect(self, tt: TokenType, msg: str = "") -> Optional[Token]:
        tok = self._match(tt)
        if tok:
            return tok
        cur = self._cur()
        err_msg = msg or f"Expected {TOKEN_DISPLAY.get(tt, tt.name)}, got {TOKEN_DISPLAY.get(cur.type, cur.type.name)}"
        self.errors.append(ParseError(err_msg, cur.line, cur.col))
        return None

    def _error(self, msg: str):
        cur = self._cur()
        self.errors.append(ParseError(msg, cur.line, cur.col))

    def _sync_to_statement(self):
        sync_tokens = {
            TokenType.SEMICOLON, TokenType.RBRACE,
            TokenType.INT_KW, TokenType.FLOAT_KW, TokenType.BOOL_KW,
            TokenType.STRING_KW, TokenType.VOID_KW,
            TokenType.IF, TokenType.WHILE, TokenType.FOR,
            TokenType.RETURN, TokenType.PRINT, TokenType.EOF,
        }
        while self._cur().type not in sync_tokens:
            self._advance()
        if self._cur().type == TokenType.SEMICOLON:
            self._advance()

    def _pos(self, tok: Optional[Token] = None) -> SourcePos:
        t = tok or self._cur()
        return SourcePos(t.line, t.col)

    def parse(self) -> Tuple[ASTNode, List[ParseError]]:
        program = ASTNode(ASTNodeType.PROGRAM, pos=SourcePos(1, 1))
        while self._cur().type != TokenType.EOF:
            decl = self._parse_top_level()
            if decl:
                program.children.append(decl)
            else:
                self._sync_to_statement()
        return program, self.errors

    def _parse_top_level(self) -> Optional[ASTNode]:
        if self._cur().type in TYPE_TOKENS:
            return self._parse_decl_or_func()
        self._error(f"Unexpected token '{self._cur().value}' at top level")
        self._advance()
        return None

    def _parse_decl_or_func(self) -> Optional[ASTNode]:
        type_tok = self._advance()
        ret_type = TYPE_NAMES.get(type_tok.type, 'int')
        name_tok = self._expect(TokenType.IDENTIFIER, "Expected identifier after type")
        if not name_tok:
            return None

        if self._cur().type == TokenType.LPAREN:
            return self._parse_func_def(ret_type, name_tok)
        else:
            return self._parse_var_decl_rest(ret_type, name_tok)

    def _parse_func_def(self, ret_type: str, name_tok: Token) -> Optional[ASTNode]:
        self._advance()
        params = self._parse_params()
        self._expect(TokenType.RPAREN, "Expected ')' after parameters")
        body = self._parse_block()
        if body is None:
            return None
        children = params + [body]
        return ASTNode(ASTNodeType.FUNC_DEF, children, name_tok.value,
                       self._pos(name_tok), ret_type)

    def _parse_params(self) -> List[ASTNode]:
        params = []
        if self._cur().type == TokenType.RPAREN:
            return params
        while True:
            if self._cur().type not in TYPE_TOKENS:
                self._error("Expected type in parameter")
                break
            type_tok = self._advance()
            ptype = TYPE_NAMES.get(type_tok.type, 'int')
            name_tok = self._expect(TokenType.IDENTIFIER, "Expected parameter name")
            is_array = False
            array_size = 0
            if name_tok and self._match(TokenType.LBRACKET):
                is_array = True
                size_tok = self._match(TokenType.INT_LITERAL)
                if size_tok:
                    array_size = size_tok.value
                self._expect(TokenType.RBRACKET, "Expected ']' in array parameter")
            if name_tok:
                node = ASTNode(ASTNodeType.PARAM, [], name_tok.value,
                               self._pos(name_tok), ptype)
                node.is_array = is_array
                node.array_size = array_size
                params.append(node)
            if not self._match(TokenType.COMMA):
                break
        return params

    def _parse_var_decl_rest(self, var_type: str, name_tok: Token) -> Optional[ASTNode]:
        if self._match(TokenType.LBRACKET):
            size_tok = self._expect(TokenType.INT_LITERAL, "Expected integer array size")
            self._expect(TokenType.RBRACKET, "Expected ']' after array size")
            init = None
            if self._match(TokenType.ASSIGN):
                init = self._parse_expression()
            self._expect(TokenType.SEMICOLON, "Expected ';' after array declaration")
            size_val = size_tok.value if size_tok else 0
            node = ASTNode(ASTNodeType.ARRAY_DECL, [], name_tok.value,
                           self._pos(name_tok), var_type)
            node.children.append(ASTNode(ASTNodeType.INT_LIT, [], size_val))
            if init:
                node.children.append(init)
            return node

        init = None
        if self._match(TokenType.ASSIGN):
            init = self._parse_expression()
        self._expect(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        node = ASTNode(ASTNodeType.VAR_DECL, [], name_tok.value,
                       self._pos(name_tok), var_type)
        if init:
            node.children.append(init)
        return node

    def _parse_block(self) -> Optional[ASTNode]:
        if not self._match(TokenType.LBRACE):
            self._error("Expected '{' to start block")
            return None
        block = ASTNode(ASTNodeType.BLOCK, pos=self._pos())
        while self._cur().type != TokenType.RBRACE and self._cur().type != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt:
                block.children.append(stmt)
            else:
                self._sync_to_statement()
        self._expect(TokenType.RBRACE, "Expected '}' to end block")
        return block

    def _parse_statement(self) -> Optional[ASTNode]:
        tt = self._cur().type
        if tt in TYPE_TOKENS and tt != TokenType.VOID_KW:
            return self._parse_local_decl()
        elif tt == TokenType.IF:
            return self._parse_if()
        elif tt == TokenType.WHILE:
            return self._parse_while()
        elif tt == TokenType.FOR:
            return self._parse_for()
        elif tt == TokenType.RETURN:
            return self._parse_return()
        elif tt == TokenType.PRINT:
            return self._parse_print()
        elif tt == TokenType.LBRACE:
            return self._parse_block()
        elif tt == TokenType.IDENTIFIER:
            return self._parse_expr_or_assign_stmt()
        else:
            self._error(f"Unexpected token '{self._cur().value}'")
            self._advance()
            return None

    def _parse_local_decl(self) -> Optional[ASTNode]:
        type_tok = self._advance()
        var_type = TYPE_NAMES.get(type_tok.type, 'int')
        name_tok = self._expect(TokenType.IDENTIFIER, "Expected identifier")
        if not name_tok:
            return None
        return self._parse_var_decl_rest(var_type, name_tok)

    def _parse_if(self) -> Optional[ASTNode]:
        self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'if'")
        cond = self._parse_expression()
        self._expect(TokenType.RPAREN, "Expected ')' after condition")
        then_body = self._parse_statement()
        else_body = None
        if self._match(TokenType.ELSE):
            else_body = self._parse_statement()
        node = ASTNode(ASTNodeType.IF, [], pos=self._pos())
        if cond:
            node.children.append(cond)
        if then_body:
            node.children.append(then_body)
        if else_body:
            node.children.append(else_body)
        return node

    def _parse_while(self) -> Optional[ASTNode]:
        self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'while'")
        cond = self._parse_expression()
        self._expect(TokenType.RPAREN, "Expected ')' after condition")
        body = self._parse_statement()
        node = ASTNode(ASTNodeType.WHILE, [], pos=self._pos())
        if cond:
            node.children.append(cond)
        if body:
            node.children.append(body)
        return node

    def _parse_for(self) -> Optional[ASTNode]:
        self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'for'")

        if self._cur().type in TYPE_TOKENS and self._cur().type != TokenType.VOID_KW:
            init = self._parse_local_decl()
        elif self._cur().type != TokenType.SEMICOLON:
            init = self._parse_expr_or_assign_stmt()
        else:
            init = None
            self._advance()

        cond = None
        if self._cur().type != TokenType.SEMICOLON:
            cond = self._parse_expression()
        self._expect(TokenType.SEMICOLON, "Expected ';' after for condition")

        update = None
        if self._cur().type != TokenType.RPAREN:
            update = self._parse_expr_or_assign_stmt_no_semi()
        self._expect(TokenType.RPAREN, "Expected ')' after for clauses")

        body = self._parse_statement()
        node = ASTNode(ASTNodeType.FOR, [], pos=self._pos())
        if init:
            node.children.append(init)
        if cond:
            node.children.append(cond)
        if update:
            node.children.append(update)
        else:
            node.children.append(ASTNode(ASTNodeType.BLOCK, pos=self._pos()))
        if body:
            node.children.append(body)
        return node

    def _parse_return(self) -> Optional[ASTNode]:
        self._advance()
        value = None
        if self._cur().type != TokenType.SEMICOLON:
            value = self._parse_expression()
        self._expect(TokenType.SEMICOLON, "Expected ';' after return")
        node = ASTNode(ASTNodeType.RETURN, [], pos=self._pos())
        if value:
            node.children.append(value)
        return node

    def _parse_print(self) -> Optional[ASTNode]:
        self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'print'")
        expr = self._parse_expression()
        self._expect(TokenType.RPAREN, "Expected ')' after print argument")
        self._expect(TokenType.SEMICOLON, "Expected ';' after print")
        node = ASTNode(ASTNodeType.PRINT, [], pos=self._pos())
        if expr:
            node.children.append(expr)
        return node

    def _parse_expr_or_assign_stmt(self) -> Optional[ASTNode]:
        expr = self._parse_expression()
        if expr is None:
            self._expect(TokenType.SEMICOLON, "Expected ';'")
            return None
        if self._match(TokenType.ASSIGN):
            value = self._parse_expression()
            self._expect(TokenType.SEMICOLON, "Expected ';' after assignment")
            node = ASTNode(ASTNodeType.ASSIGN, [], pos=expr.pos)
            node.children.append(expr)
            if value:
                node.children.append(value)
            return node
        self._expect(TokenType.SEMICOLON, "Expected ';' or '=' after expression")
        return expr

    def _parse_expr_or_assign_stmt_no_semi(self) -> Optional[ASTNode]:
        expr = self._parse_expression()
        if expr is None:
            return None
        if self._match(TokenType.ASSIGN):
            value = self._parse_expression()
            node = ASTNode(ASTNodeType.ASSIGN, [], pos=expr.pos)
            node.children.append(expr)
            if value:
                node.children.append(value)
            return node
        return expr

    def _parse_expression(self) -> Optional[ASTNode]:
        return self._parse_or()

    def _parse_or(self) -> Optional[ASTNode]:
        left = self._parse_and()
        while self._cur().type == TokenType.OR:
            op_tok = self._advance()
            right = self._parse_and()
            node = ASTNode(ASTNodeType.BINARY_OP, [], op_tok.value, self._pos(op_tok))
            if left:
                node.children.append(left)
            if right:
                node.children.append(right)
            left = node
        return left

    def _parse_and(self) -> Optional[ASTNode]:
        left = self._parse_equality()
        while self._cur().type == TokenType.AND:
            op_tok = self._advance()
            right = self._parse_equality()
            node = ASTNode(ASTNodeType.BINARY_OP, [], op_tok.value, self._pos(op_tok))
            if left:
                node.children.append(left)
            if right:
                node.children.append(right)
            left = node
        return left

    def _parse_equality(self) -> Optional[ASTNode]:
        left = self._parse_comparison()
        while self._cur().type in (TokenType.EQ, TokenType.NEQ):
            op_tok = self._advance()
            right = self._parse_comparison()
            node = ASTNode(ASTNodeType.BINARY_OP, [], op_tok.value, self._pos(op_tok))
            if left:
                node.children.append(left)
            if right:
                node.children.append(right)
            left = node
        return left

    def _parse_comparison(self) -> Optional[ASTNode]:
        left = self._parse_addition()
        while self._cur().type in (TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op_tok = self._advance()
            right = self._parse_addition()
            node = ASTNode(ASTNodeType.BINARY_OP, [], op_tok.value, self._pos(op_tok))
            if left:
                node.children.append(left)
            if right:
                node.children.append(right)
            left = node
        return left

    def _parse_addition(self) -> Optional[ASTNode]:
        left = self._parse_multiplication()
        while self._cur().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self._advance()
            right = self._parse_multiplication()
            node = ASTNode(ASTNodeType.BINARY_OP, [], op_tok.value, self._pos(op_tok))
            if left:
                node.children.append(left)
            if right:
                node.children.append(right)
            left = node
        return left

    def _parse_multiplication(self) -> Optional[ASTNode]:
        left = self._parse_unary()
        while self._cur().type in (TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op_tok = self._advance()
            right = self._parse_unary()
            node = ASTNode(ASTNodeType.BINARY_OP, [], op_tok.value, self._pos(op_tok))
            if left:
                node.children.append(left)
            if right:
                node.children.append(right)
            left = node
        return left

    def _parse_unary(self) -> Optional[ASTNode]:
        if self._cur().type == TokenType.NOT:
            op_tok = self._advance()
            operand = self._parse_unary()
            node = ASTNode(ASTNodeType.UNARY_OP, [], op_tok.value, self._pos(op_tok))
            if operand:
                node.children.append(operand)
            return node
        if self._cur().type == TokenType.MINUS:
            op_tok = self._advance()
            operand = self._parse_unary()
            node = ASTNode(ASTNodeType.UNARY_OP, [], op_tok.value, self._pos(op_tok))
            if operand:
                node.children.append(operand)
            return node
        return self._parse_postfix()

    def _parse_postfix(self) -> Optional[ASTNode]:
        expr = self._parse_primary()
        while True:
            if self._cur().type == TokenType.LBRACKET:
                self._advance()
                index = self._parse_expression()
                self._expect(TokenType.RBRACKET, "Expected ']' after index")
                node = ASTNode(ASTNodeType.ARRAY_ACCESS, [], pos=expr.pos if expr else self._pos())
                if expr:
                    node.children.append(expr)
                if index:
                    node.children.append(index)
                expr = node
            elif self._cur().type == TokenType.LPAREN and expr and expr.type == ASTNodeType.IDENTIFIER:
                self._advance()
                args = self._parse_args()
                self._expect(TokenType.RPAREN, "Expected ')' after arguments")
                node = ASTNode(ASTNodeType.CALL, args, expr.value, expr.pos)
                expr = node
            else:
                break
        return expr

    def _parse_args(self) -> List[ASTNode]:
        args = []
        if self._cur().type == TokenType.RPAREN:
            return args
        while True:
            arg = self._parse_expression()
            if arg:
                args.append(arg)
            if not self._match(TokenType.COMMA):
                break
        return args

    def _parse_primary(self) -> Optional[ASTNode]:
        tok = self._cur()
        if tok.type == TokenType.INT_LITERAL:
            self._advance()
            return ASTNode(ASTNodeType.INT_LIT, [], tok.value, self._pos(tok))
        elif tok.type == TokenType.FLOAT_LITERAL:
            self._advance()
            return ASTNode(ASTNodeType.FLOAT_LIT, [], tok.value, self._pos(tok))
        elif tok.type == TokenType.TRUE or tok.type == TokenType.FALSE:
            self._advance()
            return ASTNode(ASTNodeType.BOOL_LIT, [], tok.value, self._pos(tok))
        elif tok.type == TokenType.STRING_LITERAL:
            self._advance()
            return ASTNode(ASTNodeType.STRING_LIT, [], tok.value, self._pos(tok))
        elif tok.type == TokenType.IDENTIFIER:
            self._advance()
            return ASTNode(ASTNodeType.IDENTIFIER, [], tok.value, self._pos(tok))
        elif tok.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr
        else:
            self._error(f"Unexpected token '{tok.value}' in expression")
            self._advance()
            return None


@dataclass
class SymbolEntry:
    name: str
    type_name: str
    is_array: bool = False
    array_size: int = 0
    is_param: bool = False
    is_used: bool = False
    pos: Optional[SourcePos] = None


@dataclass
class FuncSignature:
    name: str
    param_types: List[str]
    return_type: str
    pos: Optional[SourcePos] = None


@dataclass
class Scope:
    parent: Optional['Scope']
    level: int
    symbols: Dict[str, SymbolEntry] = field(default_factory=dict)

    def define(self, entry: SymbolEntry) -> bool:
        if entry.name in self.symbols:
            return False
        self.symbols[entry.name] = entry
        return True

    def lookup(self, name: str) -> Optional[SymbolEntry]:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None


@dataclass
class TypeCheckError:
    message: str
    line: int
    col: int
    severity: str = "error"


class TypeChecker:
    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.errors: List[TypeCheckError] = []
        self.global_scope = Scope(None, 0)
        self.current_scope = self.global_scope
        self.func_sigs: Dict[str, FuncSignature] = {}
        self.current_func: Optional[str] = None
        self.scope_tree: List[Tuple[Scope, List[Tuple[str, SymbolEntry]]]] = []
        self._collect_scope(self.global_scope)

    def _collect_scope(self, scope: Scope):
        entries = list(scope.symbols.items())
        self.scope_tree.append((scope, entries))

    def _push_scope(self) -> Scope:
        new_scope = Scope(self.current_scope, self.current_scope.level + 1)
        self.current_scope = new_scope
        self._collect_scope(new_scope)
        return new_scope

    def _pop_scope(self) -> List[Tuple[str, SymbolEntry]]:
        unused = []
        for name, entry in self.current_scope.symbols.items():
            if not entry.is_used and not entry.is_param:
                unused.append((name, entry))
        self.current_scope = self.current_scope.parent
        return unused

    def _error(self, msg: str, pos: Optional[SourcePos], severity: str = "error"):
        line = pos.line if pos else 0
        col = pos.col if pos else 0
        self.errors.append(TypeCheckError(msg, line, col, severity))

    def check(self) -> List[TypeCheckError]:
        for child in self.ast.children:
            if child.type == ASTNodeType.FUNC_DEF:
                self._register_func(child)
            elif child.type in (ASTNodeType.VAR_DECL, ASTNodeType.ARRAY_DECL):
                self._check_global_decl(child)

        for child in self.ast.children:
            if child.type == ASTNodeType.FUNC_DEF:
                self._check_func_def(child)
            elif child.type in (ASTNodeType.VAR_DECL, ASTNodeType.ARRAY_DECL):
                self._check_decl_type(child)

        self._check_unused_in_scope(self.global_scope)
        return self.errors

    def _register_func(self, node: ASTNode):
        name = node.value
        param_types = [p.inferred_type for p in node.children if p.type == ASTNodeType.PARAM]
        ret_type = node.inferred_type or 'void'
        if name in self.func_sigs:
            self._error(f"Duplicate function definition '{name}'", node.pos)
            return
        self.func_sigs[name] = FuncSignature(name, param_types, ret_type, node.pos)
        entry = SymbolEntry(name, 'func', pos=node.pos)
        self.global_scope.define(entry)

    def _check_global_decl(self, node: ASTNode):
        name = node.value
        type_name = node.inferred_type or 'int'
        is_array = node.type == ASTNodeType.ARRAY_DECL
        array_size = 0
        if is_array and node.children:
            array_size = node.children[0].value if node.children else 0
        entry = SymbolEntry(name, type_name, is_array, array_size, pos=node.pos)
        if not self.global_scope.define(entry):
            self._error(f"Duplicate declaration of '{name}'", node.pos)

    def _check_decl_type(self, node: ASTNode):
        type_name = node.inferred_type
        if type_name not in ('int', 'float', 'bool', 'string', 'void'):
            self._error(f"Unknown type '{type_name}'", node.pos)
        if node.type == ASTNodeType.VAR_DECL and node.children:
            init_type = self._check_expr(node.children[0])
            if init_type and init_type != type_name:
                if not self._is_implicit_convertible(type_name, init_type):
                    self._error(
                        f"Type mismatch: cannot assign '{init_type}' to '{type_name}'",
                        node.pos)

    def _is_implicit_convertible(self, target: str, source: str) -> bool:
        if target == 'float' and source == 'int':
            return True
        return False

    def _check_func_def(self, node: ASTNode):
        name = node.value
        self.current_func = name
        func_scope = self._push_scope()

        params = [c for c in node.children if c.type == ASTNodeType.PARAM]
        body = node.children[-1] if node.children else None

        for param in params:
            ptype = param.inferred_type or 'int'
            is_arr = getattr(param, 'is_array', False)
            arr_size = getattr(param, 'array_size', 0)
            entry = SymbolEntry(param.value, ptype, is_array=is_arr,
                                array_size=arr_size, is_param=True, pos=param.pos)
            if not func_scope.define(entry):
                self._error(f"Duplicate parameter '{param.value}'", param.pos)

        if body and body.type == ASTNodeType.BLOCK:
            self._check_block(body)

        unused = self._pop_scope()
        for uname, uentry in unused:
            self._error(f"Unused variable '{uname}'", uentry.pos, "warning")

        self.current_func = None

    def _check_block(self, node: ASTNode):
        for child in node.children:
            self._check_stmt(child)

    def _check_stmt(self, node: ASTNode):
        if node is None:
            return
        t = node.type
        if t == ASTNodeType.VAR_DECL or t == ASTNodeType.ARRAY_DECL:
            self._check_local_decl(node)
        elif t == ASTNodeType.ASSIGN:
            self._check_assign(node)
        elif t == ASTNodeType.IF:
            self._check_if(node)
        elif t == ASTNodeType.WHILE:
            self._check_while(node)
        elif t == ASTNodeType.FOR:
            self._check_for(node)
        elif t == ASTNodeType.RETURN:
            self._check_return(node)
        elif t == ASTNodeType.PRINT:
            self._check_print(node)
        elif t == ASTNodeType.BLOCK:
            self._push_scope()
            self._check_block(node)
            unused = self._pop_scope()
            for uname, uentry in unused:
                self._error(f"Unused variable '{uname}'", uentry.pos, "warning")
        elif t in (ASTNodeType.BINARY_OP, ASTNodeType.UNARY_OP,
                   ASTNodeType.CALL, ASTNodeType.ARRAY_ACCESS,
                   ASTNodeType.INT_LIT, ASTNodeType.FLOAT_LIT,
                   ASTNodeType.BOOL_LIT, ASTNodeType.STRING_LIT,
                   ASTNodeType.IDENTIFIER):
            self._check_expr(node)

    def _check_local_decl(self, node: ASTNode):
        name = node.value
        type_name = node.inferred_type or 'int'
        is_array = node.type == ASTNodeType.ARRAY_DECL
        array_size = 0
        if is_array and node.children:
            array_size = node.children[0].value

        entry = SymbolEntry(name, type_name, is_array, array_size, pos=node.pos)
        if not self.current_scope.define(entry):
            self._error(f"Duplicate declaration of '{name}' in current scope", node.pos)

        if node.type == ASTNodeType.VAR_DECL and node.children:
            init_type = self._check_expr(node.children[0])
            if init_type and init_type != type_name:
                if not self._is_implicit_convertible(type_name, init_type):
                    self._error(
                        f"Type mismatch: cannot assign '{init_type}' to variable '{name}' of type '{type_name}'",
                        node.pos)

    def _check_assign(self, node: ASTNode):
        if len(node.children) < 2:
            return
        target = node.children[0]
        value = node.children[1]

        target_type = self._check_lvalue(target)
        value_type = self._check_expr(value)

        if target_type and value_type:
            if target_type != value_type:
                if not self._is_implicit_convertible(target_type, value_type):
                    self._error(
                        f"Type mismatch: cannot assign '{value_type}' to '{target_type}'",
                        node.pos)

    def _check_lvalue(self, node: ASTNode) -> Optional[str]:
        if node.type == ASTNodeType.IDENTIFIER:
            entry = self.current_scope.lookup(node.value)
            if not entry:
                self._error(f"Undeclared variable '{node.value}'", node.pos)
                return None
            entry.is_used = True
            node.inferred_type = entry.type_name
            return entry.type_name
        elif node.type == ASTNodeType.ARRAY_ACCESS:
            arr_type = self._check_lvalue(node.children[0]) if node.children else None
            if len(node.children) > 1:
                idx_type = self._check_expr(node.children[1])
                if idx_type and idx_type != 'int':
                    self._error(
                        f"Array index must be 'int', got '{idx_type}'",
                        node.children[1].pos)
            node.inferred_type = arr_type
            return arr_type
        else:
            self._error("Invalid assignment target", node.pos)
            return None

    def _check_if(self, node: ASTNode):
        if len(node.children) > 0 and node.children[0]:
            cond_type = self._check_expr(node.children[0])
            if cond_type and cond_type != 'bool':
                self._error(
                    f"If condition must be 'bool', got '{cond_type}'",
                    node.children[0].pos)
        if len(node.children) > 1 and node.children[1]:
            self._check_stmt(node.children[1])
        if len(node.children) > 2 and node.children[2]:
            self._check_stmt(node.children[2])

    def _check_while(self, node: ASTNode):
        if len(node.children) > 0 and node.children[0]:
            cond_type = self._check_expr(node.children[0])
            if cond_type and cond_type != 'bool':
                self._error(
                    f"While condition must be 'bool', got '{cond_type}'",
                    node.children[0].pos)
        if len(node.children) > 1 and node.children[1]:
            self._check_stmt(node.children[1])

    def _check_for(self, node: ASTNode):
        self._push_scope()
        if len(node.children) > 0 and node.children[0]:
            self._check_stmt(node.children[0])
        if len(node.children) > 1 and node.children[1]:
            cond_type = self._check_expr(node.children[1])
            if cond_type and cond_type != 'bool':
                self._error(
                    f"For condition must be 'bool', got '{cond_type}'",
                    node.children[1].pos)
        if len(node.children) > 2 and node.children[2]:
            self._check_stmt(node.children[2])
        if len(node.children) > 3 and node.children[3]:
            self._check_stmt(node.children[3])
        unused = self._pop_scope()
        for uname, uentry in unused:
            self._error(f"Unused variable '{uname}'", uentry.pos, "warning")

    def _check_return(self, node: ASTNode):
        if not self.current_func:
            self._error("Return statement outside function", node.pos)
            return
        sig = self.func_sigs.get(self.current_func)
        if not sig:
            return
        ret_type = sig.return_type
        if len(node.children) > 0 and node.children[0]:
            actual_type = self._check_expr(node.children[0])
            if actual_type and ret_type != actual_type:
                if not self._is_implicit_convertible(ret_type, actual_type):
                    self._error(
                        f"Return type mismatch: expected '{ret_type}', got '{actual_type}'",
                        node.pos)
        else:
            if ret_type != 'void':
                self._error(
                    f"Function '{self.current_func}' should return '{ret_type}'",
                    node.pos)

    def _check_print(self, node: ASTNode):
        if node.children:
            self._check_expr(node.children[0])

    def _check_expr(self, node: ASTNode) -> Optional[str]:
        if node is None:
            return None
        t = node.type

        if t == ASTNodeType.INT_LIT:
            node.inferred_type = 'int'
            return 'int'
        elif t == ASTNodeType.FLOAT_LIT:
            node.inferred_type = 'float'
            return 'float'
        elif t == ASTNodeType.BOOL_LIT:
            node.inferred_type = 'bool'
            return 'bool'
        elif t == ASTNodeType.STRING_LIT:
            node.inferred_type = 'string'
            return 'string'
        elif t == ASTNodeType.IDENTIFIER:
            entry = self.current_scope.lookup(node.value)
            if not entry:
                self._error(f"Undeclared variable '{node.value}'", node.pos)
                return None
            entry.is_used = True
            node.inferred_type = entry.type_name
            return entry.type_name
        elif t == ASTNodeType.BINARY_OP:
            return self._check_binary(node)
        elif t == ASTNodeType.UNARY_OP:
            return self._check_unary(node)
        elif t == ASTNodeType.CALL:
            return self._check_call(node)
        elif t == ASTNodeType.ARRAY_ACCESS:
            return self._check_array_access(node)

        return None

    def _check_binary(self, node: ASTNode) -> Optional[str]:
        left_type = self._check_expr(node.children[0]) if len(node.children) > 0 else None
        right_type = self._check_expr(node.children[1]) if len(node.children) > 1 else None
        op = node.value

        if op in ('+', '-', '*', '/', '%'):
            if left_type and right_type:
                if op == '+':
                    if left_type == 'string' and right_type == 'string':
                        node.inferred_type = 'string'
                        return 'string'
                if op == '%':
                    if left_type != 'int' or right_type != 'int':
                        self._error(
                            f"Operator '{op}' requires 'int' operands, got '{left_type}' and '{right_type}'",
                            node.pos)
                    node.inferred_type = 'int'
                    return 'int'
                if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                    self._error(
                        f"Operator '{op}' requires numeric operands, got '{left_type}' and '{right_type}'",
                        node.pos)
                result = 'float' if 'float' in (left_type, right_type) else 'int'
                node.inferred_type = result
                return result
            return left_type or right_type

        elif op in ('==', '!='):
            if left_type and right_type and left_type != right_type:
                self._error(
                    f"Cannot compare '{left_type}' with '{right_type}'",
                    node.pos)
            node.inferred_type = 'bool'
            return 'bool'

        elif op in ('<', '>', '<=', '>='):
            if left_type and right_type:
                if left_type not in ('int', 'float') or right_type not in ('int', 'float'):
                    self._error(
                        f"Comparison requires numeric operands, got '{left_type}' and '{right_type}'",
                        node.pos)
            node.inferred_type = 'bool'
            return 'bool'

        elif op in ('&&', '||'):
            if left_type and left_type != 'bool':
                self._error(f"Logical operator requires 'bool', got '{left_type}'", node.pos)
            if right_type and right_type != 'bool':
                self._error(f"Logical operator requires 'bool', got '{right_type}'", node.pos)
            node.inferred_type = 'bool'
            return 'bool'

        return None

    def _check_unary(self, node: ASTNode) -> Optional[str]:
        operand_type = self._check_expr(node.children[0]) if node.children else None
        op = node.value

        if op == '!':
            if operand_type and operand_type != 'bool':
                self._error(f"Logical NOT requires 'bool', got '{operand_type}'", node.pos)
            node.inferred_type = 'bool'
            return 'bool'
        elif op == '-':
            if operand_type and operand_type not in ('int', 'float'):
                self._error(f"Unary minus requires numeric type, got '{operand_type}'", node.pos)
            result = operand_type or 'int'
            node.inferred_type = result
            return result

        return operand_type

    def _check_call(self, node: ASTNode) -> Optional[str]:
        name = node.value
        sig = self.func_sigs.get(name)
        if not sig:
            entry = self.current_scope.lookup(name)
            if not entry:
                self._error(f"Undeclared function '{name}'", node.pos)
                return None
            self._error(f"'{name}' is not a function", node.pos)
            return None

        func_entry = self.global_scope.lookup(name)
        if func_entry:
            func_entry.is_used = True

        arg_types = []
        for arg in node.children:
            at = self._check_expr(arg)
            if at:
                arg_types.append(at)

        if len(arg_types) != len(sig.param_types):
            self._error(
                f"Function '{name}' expects {len(sig.param_types)} arguments, got {len(arg_types)}",
                node.pos)
        else:
            for i, (actual, expected) in enumerate(zip(arg_types, sig.param_types)):
                if actual != expected:
                    if not self._is_implicit_convertible(expected, actual):
                        self._error(
                            f"Argument {i+1} of '{name}': expected '{expected}', got '{actual}'",
                            node.pos)

        node.inferred_type = sig.return_type
        return sig.return_type

    def _check_array_access(self, node: ASTNode) -> Optional[str]:
        if len(node.children) > 0:
            arr_type = self._check_expr(node.children[0])
        else:
            arr_type = None
        if len(node.children) > 1:
            idx_type = self._check_expr(node.children[1])
            if idx_type and idx_type != 'int':
                self._error(
                    f"Array index must be 'int', got '{idx_type}'",
                    node.children[1].pos)
        node.inferred_type = arr_type
        return arr_type

    def _check_unused_in_scope(self, scope: Scope):
        for name, entry in scope.symbols.items():
            if not entry.is_used and entry.type_name != 'func' and not entry.is_param:
                self._error(f"Unused variable '{name}'", entry.pos, "warning")

    def get_scopes_info(self) -> List[Dict]:
        result = []
        self._collect_scope_info(self.global_scope, "global", result)
        return result

    def _collect_scope_info(self, scope: Scope, name: str, result: List[Dict]):
        entries = []
        for sname, entry in scope.symbols.items():
            entries.append({
                "name": sname,
                "type": entry.type_name,
                "is_array": entry.is_array,
                "is_used": entry.is_used,
                "is_param": entry.is_param,
            })
        result.append({"scope": name, "level": scope.level, "symbols": entries})


class IRGenerator:
    BIN_OP_MAP = {
        '+': IROp.ADD, '-': IROp.SUB, '*': IROp.MUL, '/': IROp.DIV, '%': IROp.MOD,
        '==': IROp.EQ, '!=': IROp.NEQ, '<': IROp.LT, '>': IROp.GT,
        '<=': IROp.LE, '>=': IROp.GE, '&&': IROp.AND, '||': IROp.OR,
    }

    def __init__(self, ast: ASTNode):
        self.ast = ast
        self.temp_counter = 0
        self.label_counter = 0
        self.function_irs: Dict[str, FunctionIR] = {}
        self.current_func: Optional[FunctionIR] = None

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self, prefix: str = "L") -> str:
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    def emit(self, op: IROp, result: Optional[str] = None,
             arg1: Optional[str] = None, arg2: Optional[str] = None,
             extra: Optional[Any] = None):
        if self.current_func is None:
            return
        self.current_func.instructions.append(IRInst(op, result, arg1, arg2, extra))

    def generate(self) -> Dict[str, FunctionIR]:
        for child in self.ast.children:
            if child.type == ASTNodeType.FUNC_DEF:
                self._generate_function(child)
        return self.function_irs

    def _generate_function(self, node: ASTNode):
        func_name = node.value
        self.temp_counter = 0
        self.label_counter = 0
        self.current_func = FunctionIR(name=func_name)
        self.function_irs[func_name] = self.current_func

        entry_label = self.new_label()
        self.emit(IROp.LABEL, arg1=entry_label)

        body = node.children[-1] if node.children else None
        if body and body.type == ASTNodeType.BLOCK:
            self._generate_block(body)

        if not self.current_func.instructions or self.current_func.instructions[-1].op not in (IROp.RETURN, IROp.JUMP):
            self.emit(IROp.RETURN)

    def _generate_block(self, node: ASTNode):
        for child in node.children:
            self._generate_stmt(child)

    def _generate_stmt(self, node: ASTNode):
        if node is None:
            return
        t = node.type
        if t == ASTNodeType.VAR_DECL:
            self._generate_var_decl(node)
        elif t == ASTNodeType.ARRAY_DECL:
            pass
        elif t == ASTNodeType.ASSIGN:
            self._generate_assign(node)
        elif t == ASTNodeType.IF:
            self._generate_if(node)
        elif t == ASTNodeType.WHILE:
            self._generate_while(node)
        elif t == ASTNodeType.FOR:
            self._generate_for(node)
        elif t == ASTNodeType.RETURN:
            self._generate_return(node)
        elif t == ASTNodeType.PRINT:
            self._generate_print(node)
        elif t == ASTNodeType.BLOCK:
            self._generate_block(node)
        elif t in (ASTNodeType.BINARY_OP, ASTNodeType.UNARY_OP,
                   ASTNodeType.CALL, ASTNodeType.ARRAY_ACCESS,
                   ASTNodeType.INT_LIT, ASTNodeType.FLOAT_LIT,
                   ASTNodeType.BOOL_LIT, ASTNodeType.STRING_LIT,
                   ASTNodeType.IDENTIFIER):
            self._generate_expr(node)

    def _generate_var_decl(self, node: ASTNode):
        name = node.value
        if node.children:
            init_val = self._generate_expr(node.children[0])
            self.emit(IROp.ASSIGN, result=name, arg1=init_val)

    def _generate_assign(self, node: ASTNode):
        target = node.children[0]
        value = self._generate_expr(node.children[1])
        if target.type == ASTNodeType.IDENTIFIER:
            self.emit(IROp.ASSIGN, result=target.value, arg1=value)
        elif target.type == ASTNodeType.ARRAY_ACCESS:
            arr_name = target.children[0].value
            idx = self._generate_expr(target.children[1])
            self.emit(IROp.ARRAY_STORE, result=value, arg1=arr_name, arg2=idx)

    def _generate_if(self, node: ASTNode):
        cond = self._generate_expr(node.children[0])
        then_label = self.new_label()
        else_label = self.new_label()
        end_label = self.new_label()

        if len(node.children) > 2:
            self.emit(IROp.JUMP_IF_NOT, arg1=cond, arg2=else_label)
            self.emit(IROp.LABEL, arg1=then_label)
            self._generate_stmt(node.children[1])
            self.emit(IROp.JUMP, arg1=end_label)
            self.emit(IROp.LABEL, arg1=else_label)
            self._generate_stmt(node.children[2])
        else:
            self.emit(IROp.JUMP_IF_NOT, arg1=cond, arg2=end_label)
            self.emit(IROp.LABEL, arg1=then_label)
            self._generate_stmt(node.children[1])
        self.emit(IROp.LABEL, arg1=end_label)

    def _generate_while(self, node: ASTNode):
        cond_label = self.new_label("W")
        body_label = self.new_label("W")
        end_label = self.new_label("W")

        self.emit(IROp.LABEL, arg1=cond_label)
        cond = self._generate_expr(node.children[0])
        self.emit(IROp.JUMP_IF_NOT, arg1=cond, arg2=end_label)
        self.emit(IROp.LABEL, arg1=body_label)
        self._generate_stmt(node.children[1])
        self.emit(IROp.JUMP, arg1=cond_label)
        self.emit(IROp.LABEL, arg1=end_label)

    def _generate_for(self, node: ASTNode):
        init = node.children[0] if len(node.children) > 0 else None
        cond = node.children[1] if len(node.children) > 1 else None
        update = node.children[2] if len(node.children) > 2 else None
        body = node.children[3] if len(node.children) > 3 else None

        if init:
            self._generate_stmt(init)

        cond_label = self.new_label("F")
        body_label = self.new_label("F")
        end_label = self.new_label("F")

        self.emit(IROp.LABEL, arg1=cond_label)
        if cond:
            cond_val = self._generate_expr(cond)
            self.emit(IROp.JUMP_IF_NOT, arg1=cond_val, arg2=end_label)
        self.emit(IROp.LABEL, arg1=body_label)
        if body:
            self._generate_stmt(body)
        if update and update.children:
            self._generate_stmt(update)
        self.emit(IROp.JUMP, arg1=cond_label)
        self.emit(IROp.LABEL, arg1=end_label)

    def _generate_return(self, node: ASTNode):
        if node.children:
            val = self._generate_expr(node.children[0])
            self.emit(IROp.RETURN, arg1=val)
        else:
            self.emit(IROp.RETURN)

    def _generate_print(self, node: ASTNode):
        if node.children:
            val = self._generate_expr(node.children[0])
            self.emit(IROp.PRINT, arg1=val)

    def _generate_expr(self, node: ASTNode) -> str:
        if node is None:
            return ""
        t = node.type

        if t == ASTNodeType.INT_LIT:
            temp = self.new_temp()
            self.emit(IROp.ASSIGN, result=temp, arg1=str(node.value))
            return temp
        elif t == ASTNodeType.FLOAT_LIT:
            temp = self.new_temp()
            self.emit(IROp.ASSIGN, result=temp, arg1=str(node.value))
            return temp
        elif t == ASTNodeType.BOOL_LIT:
            temp = self.new_temp()
            self.emit(IROp.ASSIGN, result=temp, arg1="true" if node.value else "false")
            return temp
        elif t == ASTNodeType.STRING_LIT:
            temp = self.new_temp()
            self.emit(IROp.ASSIGN, result=temp, arg1=repr(node.value))
            return temp
        elif t == ASTNodeType.IDENTIFIER:
            return node.value
        elif t == ASTNodeType.BINARY_OP:
            return self._generate_binary(node)
        elif t == ASTNodeType.UNARY_OP:
            return self._generate_unary(node)
        elif t == ASTNodeType.CALL:
            return self._generate_call(node)
        elif t == ASTNodeType.ARRAY_ACCESS:
            return self._generate_array_access(node)

        return ""

    def _generate_binary(self, node: ASTNode) -> str:
        left = self._generate_expr(node.children[0])
        right = self._generate_expr(node.children[1])
        op = node.value
        ir_op = self.BIN_OP_MAP.get(op)
        if ir_op:
            temp = self.new_temp()
            self.emit(ir_op, result=temp, arg1=left, arg2=right)
            return temp
        return left

    def _generate_unary(self, node: ASTNode) -> str:
        operand = self._generate_expr(node.children[0])
        op = node.value
        if op == '!':
            temp = self.new_temp()
            self.emit(IROp.NOT, result=temp, arg1=operand)
            return temp
        elif op == '-':
            temp = self.new_temp()
            self.emit(IROp.NEG, result=temp, arg1=operand)
            return temp
        return operand

    def _generate_call(self, node: ASTNode) -> str:
        func_name = node.value
        args = []
        for arg in node.children:
            arg_val = self._generate_expr(arg)
            args.append(arg_val)
            self.emit(IROp.PARAM, arg1=arg_val)
        temp = self.new_temp()
        self.emit(IROp.CALL, result=temp, arg1=func_name, extra=args)
        return temp

    def _generate_array_access(self, node: ASTNode) -> str:
        arr_name = node.children[0].value
        idx = self._generate_expr(node.children[1])
        temp = self.new_temp()
        self.emit(IROp.ARRAY_LOAD, result=temp, arg1=arr_name, arg2=idx)
        return temp


class CFGBuilder:
    def build(self, func_ir: FunctionIR) -> List[BasicBlock]:
        instructions = func_ir.instructions
        if not instructions:
            return []

        leader_indices = self._find_leaders(instructions)
        blocks = self._create_blocks(instructions, leader_indices)
        self._build_edges(blocks, instructions, leader_indices)
        return blocks

    def _find_leaders(self, instructions: List[IRInst]) -> set:
        leaders = {0}
        for i, inst in enumerate(instructions):
            if inst.op in (IROp.JUMP, IROp.JUMP_IF, IROp.JUMP_IF_NOT):
                if i + 1 < len(instructions):
                    leaders.add(i + 1)
                label = inst.arg2 if inst.op in (IROp.JUMP_IF, IROp.JUMP_IF_NOT) else inst.arg1
                for j, jn in enumerate(instructions):
                    if jn.op == IROp.LABEL and jn.arg1 == label:
                        leaders.add(j)
                        break
        return sorted(leaders)

    def _create_blocks(self, instructions: List[IRInst], leader_indices: List[int]) -> List[BasicBlock]:
        blocks = []
        for i, start in enumerate(leader_indices):
            end = leader_indices[i + 1] if i + 1 < len(leader_indices) else len(instructions)
            block_insts = instructions[start:end]
            label = block_insts[0].arg1 if block_insts and block_insts[0].op == IROp.LABEL else f"BLOCK_{i}"
            bb = BasicBlock(id=i, label=label, instructions=block_insts)
            blocks.append(bb)
        return blocks

    def _build_edges(self, blocks: List[BasicBlock], instructions: List[IRInst], leader_indices: List[int]):
        label_to_block = {}
        for bb in blocks:
            if bb.instructions and bb.instructions[0].op == IROp.LABEL:
                label_to_block[bb.instructions[0].arg1] = bb.id

        for i, bb in enumerate(blocks):
            last_inst = bb.instructions[-1] if bb.instructions else None
            if last_inst is None:
                continue

            if last_inst.op == IROp.JUMP:
                target_label = last_inst.arg1
                target_id = label_to_block.get(target_label)
                if target_id is not None:
                    bb.successors.append(target_id)
                    blocks[target_id].predecessors.append(bb.id)
                    bb.jump_condition = "unconditional"
            elif last_inst.op in (IROp.JUMP_IF, IROp.JUMP_IF_NOT):
                target_label = last_inst.arg2
                target_id = label_to_block.get(target_label)
                cond = "true" if last_inst.op == IROp.JUMP_IF else "false"
                bb.jump_condition = f"if {last_inst.arg1} is {cond}"
                if target_id is not None:
                    bb.successors.append(target_id)
                    blocks[target_id].predecessors.append(bb.id)
                if i + 1 < len(blocks):
                    bb.successors.append(i + 1)
                    blocks[i + 1].predecessors.append(bb.id)
            elif last_inst.op == IROp.RETURN:
                bb.jump_condition = "return"
            else:
                if i + 1 < len(blocks):
                    bb.successors.append(i + 1)
                    blocks[i + 1].predecessors.append(bb.id)
                    bb.jump_condition = "fallthrough"


class IROptimizer:
    SIDE_EFFECT_OPS = {
        IROp.LABEL, IROp.JUMP, IROp.JUMP_IF, IROp.JUMP_IF_NOT,
        IROp.RETURN, IROp.PRINT, IROp.PARAM, IROp.ARRAY_STORE, IROp.CALL,
    }

    def optimize(self, func_ir: FunctionIR) -> Tuple[List[IRInst], List[BasicBlock]]:
        insts = list(func_ir.instructions)
        insts = self._constant_folding(insts)
        insts = self._eliminate_dead_code(insts)

        temp_func = FunctionIR(name=func_ir.name, instructions=insts)
        cfg_builder = CFGBuilder()
        blocks = cfg_builder.build(temp_func)
        return insts, blocks

    def _is_literal(self, val: Optional[str]) -> bool:
        if val is None:
            return False
        if val in ("true", "false"):
            return True
        if val.startswith('"') and val.endswith('"'):
            return True
        try:
            float(val)
            return True
        except ValueError:
            return False

    def _parse_literal(self, val: str) -> Any:
        if val == "true":
            return True
        if val == "false":
            return False
        if val.startswith('"') and val.endswith('"'):
            return val[1:-1]
        try:
            if '.' in val:
                return float(val)
            return int(val)
        except ValueError:
            return val

    def _literal_to_str(self, val: Any) -> str:
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, str) and not (val.startswith('"') and val.endswith('"')):
            return repr(val)
        return str(val)

    def _get_uses(self, inst: IRInst) -> set:
        uses = set()
        if inst.op == IROp.LABEL:
            return uses
        if inst.op == IROp.JUMP:
            return uses
        if inst.op in (IROp.JUMP_IF, IROp.JUMP_IF_NOT):
            if inst.arg1:
                uses.add(inst.arg1)
            return uses
        if inst.op == IROp.ARRAY_STORE:
            if inst.result:
                uses.add(inst.result)
            if inst.arg1:
                uses.add(inst.arg1)
            if inst.arg2:
                uses.add(inst.arg2)
            return uses
        if inst.op == IROp.CALL:
            if inst.extra and isinstance(inst.extra, list):
                for a in inst.extra:
                    uses.add(a)
            return uses
        if inst.op == IROp.ASSIGN:
            if inst.arg1:
                uses.add(inst.arg1)
            return uses
        if inst.op in (IROp.ADD, IROp.SUB, IROp.MUL, IROp.DIV, IROp.MOD,
                       IROp.EQ, IROp.NEQ, IROp.LT, IROp.GT, IROp.LE, IROp.GE,
                       IROp.AND, IROp.OR):
            if inst.arg1:
                uses.add(inst.arg1)
            if inst.arg2:
                uses.add(inst.arg2)
            return uses
        if inst.op in (IROp.NOT, IROp.NEG, IROp.ARRAY_LOAD,
                       IROp.RETURN, IROp.PRINT, IROp.PARAM):
            if inst.arg1:
                uses.add(inst.arg1)
            return uses
        return uses

    def _get_def(self, inst: IRInst) -> Optional[str]:
        if inst.op in self.SIDE_EFFECT_OPS:
            if inst.op in (IROp.CALL,):
                return inst.result
            return None
        return inst.result

    def _constant_folding(self, insts: List[IRInst]) -> List[IRInst]:
        const_map: Dict[str, Any] = {}
        result = []
        arith_ops = {IROp.ADD, IROp.SUB, IROp.MUL, IROp.DIV, IROp.MOD}
        cmp_ops = {IROp.EQ, IROp.NEQ, IROp.LT, IROp.GT, IROp.LE, IROp.GE}
        logic_ops = {IROp.AND, IROp.OR}

        def resolve(val: Optional[str]) -> Optional[Any]:
            if val is None:
                return None
            if val in const_map:
                return const_map[val]
            if self._is_literal(val):
                return self._parse_literal(val)
            return None

        for inst in insts:
            new_inst = IRInst(inst.op, inst.result, inst.arg1, inst.arg2, inst.extra)
            folded = False

            r1 = resolve(new_inst.arg1)
            if r1 is not None and new_inst.op not in (IROp.LABEL,):
                new_inst.arg1 = self._literal_to_str(r1)
            r2 = resolve(new_inst.arg2)
            if r2 is not None:
                new_inst.arg2 = self._literal_to_str(r2)
            if new_inst.extra and isinstance(new_inst.extra, list):
                new_extra = []
                for a in new_inst.extra:
                    ra = resolve(a)
                    new_extra.append(self._literal_to_str(ra) if ra is not None else a)
                new_inst.extra = new_extra

            defn = self._get_def(new_inst)

            if new_inst.op in arith_ops and defn and self._is_literal(new_inst.arg1) and self._is_literal(new_inst.arg2):
                v1 = self._parse_literal(new_inst.arg1)
                v2 = self._parse_literal(new_inst.arg2)
                op_map = {IROp.ADD: lambda a, b: a + b, IROp.SUB: lambda a, b: a - b,
                          IROp.MUL: lambda a, b: a * b, IROp.DIV: lambda a, b: a / b,
                          IROp.MOD: lambda a, b: a % b}
                try:
                    folded_val = op_map[new_inst.op](v1, v2)
                    const_map[defn] = folded_val
                    new_inst = IRInst(IROp.ASSIGN, result=defn, arg1=self._literal_to_str(folded_val))
                    folded = True
                except (TypeError, ZeroDivisionError):
                    pass

            if not folded and new_inst.op in cmp_ops and defn and self._is_literal(new_inst.arg1) and self._is_literal(new_inst.arg2):
                v1 = self._parse_literal(new_inst.arg1)
                v2 = self._parse_literal(new_inst.arg2)
                op_map = {IROp.EQ: lambda a, b: a == b, IROp.NEQ: lambda a, b: a != b,
                          IROp.LT: lambda a, b: a < b, IROp.GT: lambda a, b: a > b,
                          IROp.LE: lambda a, b: a <= b, IROp.GE: lambda a, b: a >= b}
                try:
                    folded_val = op_map[new_inst.op](v1, v2)
                    const_map[defn] = folded_val
                    new_inst = IRInst(IROp.ASSIGN, result=defn, arg1=self._literal_to_str(folded_val))
                    folded = True
                except TypeError:
                    pass

            if not folded and new_inst.op in logic_ops and defn and self._is_literal(new_inst.arg1) and self._is_literal(new_inst.arg2):
                v1 = self._parse_literal(new_inst.arg1)
                v2 = self._parse_literal(new_inst.arg2)
                op_map = {IROp.AND: lambda a, b: a and b, IROp.OR: lambda a, b: a or b}
                try:
                    folded_val = op_map[new_inst.op](v1, v2)
                    const_map[defn] = folded_val
                    new_inst = IRInst(IROp.ASSIGN, result=defn, arg1=self._literal_to_str(folded_val))
                    folded = True
                except TypeError:
                    pass

            if not folded and new_inst.op == IROp.NOT and defn and self._is_literal(new_inst.arg1):
                v = self._parse_literal(new_inst.arg1)
                if isinstance(v, bool):
                    folded_val = not v
                    const_map[defn] = folded_val
                    new_inst = IRInst(IROp.ASSIGN, result=defn, arg1=self._literal_to_str(folded_val))
                    folded = True

            if not folded and new_inst.op == IROp.NEG and defn and self._is_literal(new_inst.arg1):
                v = self._parse_literal(new_inst.arg1)
                if isinstance(v, (int, float)):
                    folded_val = -v
                    const_map[defn] = folded_val
                    new_inst = IRInst(IROp.ASSIGN, result=defn, arg1=self._literal_to_str(folded_val))
                    folded = True

            if not folded and new_inst.op == IROp.ASSIGN and defn and self._is_literal(new_inst.arg1):
                const_map[defn] = self._parse_literal(new_inst.arg1)

            result.append(new_inst)
        return result

    def _eliminate_dead_code(self, insts: List[IRInst]) -> List[IRInst]:
        used: set = set()
        changed = True
        while changed:
            changed = False
            for inst in reversed(insts):
                defn = self._get_def(inst)
                if defn and defn in used:
                    for u in self._get_uses(inst):
                        if u not in used:
                            used.add(u)
                            changed = True
                elif inst.op in self.SIDE_EFFECT_OPS:
                    for u in self._get_uses(inst):
                        if u not in used:
                            used.add(u)
                            changed = True

        result = []
        for inst in insts:
            if inst.op in self.SIDE_EFFECT_OPS:
                result.append(inst)
                continue
            defn = self._get_def(inst)
            if defn and defn in used:
                result.append(inst)
        return result


def format_token_table(tokens: List[Token]) -> str:
    header = f"{'No.':<5} {'Type':<12} {'Value':<20} {'Line':<6} {'Col':<5}"
    sep = "-" * len(header)
    lines = [header, sep]
    for i, tok in enumerate(tokens):
        val = repr(tok.value) if isinstance(tok.value, str) and tok.type in (
            TokenType.STRING_LITERAL, TokenType.IDENTIFIER) else str(tok.value)
        lines.append(f"{i:<5} {tok.display_type():<12} {val:<20} {tok.line:<6} {tok.col:<5}")
    return '\n'.join(lines)


def format_ast_tree(node: ASTNode, indent: int = 0) -> str:
    prefix = "  " * indent
    parts = [f"{prefix}{node.type.name}"]
    if node.value is not None:
        parts[0] += f": {repr(node.value) if isinstance(node.value, str) else node.value}"
    if node.inferred_type:
        parts[0] += f" [type={node.inferred_type}]"
    if node.pos:
        parts[0] += f" @L{node.pos.line}:C{node.pos.col}"
    if node.type == ASTNodeType.FUNC_DEF and node.children:
        params = [c for c in node.children if c.type == ASTNodeType.PARAM]
        body = node.children[-1] if node.children else None
        if params:
            parts.append(f"{prefix}  params:")
            for p in params:
                parts.append(format_ast_tree(p, indent + 2))
        if body and body.type == ASTNodeType.BLOCK:
            parts.append(f"{prefix}  body:")
            parts.append(format_ast_tree(body, indent + 2))
    else:
        for child in node.children:
            if isinstance(child, ASTNode):
                parts.append(format_ast_tree(child, indent + 1))
            else:
                parts.append(f"{prefix}  {child}")
    return '\n'.join(parts)


def format_errors(errors: list, title: str = "Errors") -> str:
    if not errors:
        return f"{title}: None"
    lines = [f"{title}:"]
    errors_sorted = sorted(errors, key=lambda e: (getattr(e, 'severity', 'error'), getattr(e, 'line', 0)))
    for err in errors_sorted:
        if isinstance(err, LexerError):
            ctx = f"  | {err.context}" if err.context else ""
            lines.append(f"  [error] L{err.line}:C{err.col}: {err.message}{ctx}")
        elif isinstance(err, ParseError):
            lines.append(f"  [error] L{err.line}:C{err.col}: {err.message}")
        elif isinstance(err, TypeCheckError):
            lines.append(f"  [{err.severity}] L{err.line}:C{err.col}: {err.message}")
    return '\n'.join(lines)


def format_symbol_table(checker: TypeChecker) -> str:
    scopes_info = checker.get_scopes_info()
    lines = ["Symbol Table:"]
    for scope in scopes_info:
        lines.append(f"  Scope: {scope['scope']} (level {scope['level']})")
        if not scope['symbols']:
            lines.append("    (empty)")
        for sym in scope['symbols']:
            arr = f"[{sym.get('is_array', False)}]" if sym.get('is_array') else ""
            param = " (param)" if sym.get('is_param') else ""
            used = " [used]" if sym.get('is_used') else " [unused]"
            lines.append(f"    {sym['name']}: {sym['type']}{arr}{param}{used}")
    return '\n'.join(lines)


def format_ir(function_irs: Dict[str, FunctionIR], optimized: bool = False) -> str:
    lines = []
    for func_name, func_ir in function_irs.items():
        lines.append("=" * 60)
        lines.append(f"Function: {func_name}")
        lines.append("=" * 60)
        lines.append("")

        insts = func_ir.optimized_instructions if (optimized and func_ir.optimized_instructions is not None) else func_ir.instructions
        blocks = func_ir.optimized_basic_blocks if (optimized and func_ir.optimized_basic_blocks is not None) else func_ir.basic_blocks

        if optimized:
            lines.append("--- Optimized IR Instructions ---")
        else:
            lines.append("--- IR Instructions ---")
        for i, inst in enumerate(insts):
            lines.append(f"{i:4d}  {str(inst)}")
        lines.append("")

        lines.append("--- Basic Blocks ---")
        for bb in blocks:
            lines.append(f"Block {bb.id}: {bb.label}")
            if bb.predecessors:
                lines.append(f"  Predecessors: {bb.predecessors}")
            else:
                lines.append(f"  Predecessors: []")
            if bb.successors:
                lines.append(f"  Successors:   {bb.successors}")
            else:
                lines.append(f"  Successors:   []")
            if bb.jump_condition:
                lines.append(f"  Jump Cond:    {bb.jump_condition}")
            lines.append(f"  Instructions:")
            for inst in bb.instructions:
                lines.append(f"    {str(inst)}")
            lines.append("")
    return '\n'.join(lines)


def format_ir_compare(function_irs: Dict[str, FunctionIR]) -> str:
    lines = []
    for func_name, func_ir in function_irs.items():
        if func_ir.optimized_instructions is None:
            continue

        lines.append("=" * 80)
        lines.append(f"Function: {func_name}  (Before vs After Optimization)")
        lines.append("=" * 80)
        lines.append("")

        orig_insts = func_ir.instructions
        opt_insts = func_ir.optimized_instructions
        orig_count = len(orig_insts)
        opt_count = len(opt_insts)
        removed = orig_count - opt_count

        lines.append(f"Instruction count: {orig_count} -> {opt_count} (removed {removed}, {int(removed/orig_count*100) if orig_count > 0 else 0}%)")
        lines.append("")

        col_width = 38
        lines.append(f"{'Before':<{col_width}} | {'After':<{col_width}}")
        lines.append("-" * col_width + "-+-" + "-" * col_width)

        orig_idx = 0
        opt_idx = 0
        max_lines = max(orig_count, opt_count)
        for i in range(max_lines):
            orig_str = ""
            opt_str = ""
            if orig_idx < orig_count:
                orig_str = str(orig_insts[orig_idx])
                orig_idx += 1
            if opt_idx < opt_count:
                opt_str = str(opt_insts[opt_idx])
                opt_idx += 1
            orig_disp = (f"{i:3d} {orig_str}")[:col_width]
            opt_disp = (f"{i:3d} {opt_str}")[:col_width]
            marker = " " if orig_str == opt_str else "Δ"
            lines.append(f"{orig_disp:<{col_width}} {marker} {opt_disp:<{col_width}}")

        lines.append("")
        lines.append("--- Basic Blocks Comparison ---")
        lines.append(f"  Before: {len(func_ir.basic_blocks)} blocks")
        if func_ir.optimized_basic_blocks:
            lines.append(f"  After:  {len(func_ir.optimized_basic_blocks)} blocks")
        lines.append("")
    return '\n'.join(lines)


def build_ir_with_cfg(ast: ASTNode, do_optimize: bool = False) -> Dict[str, FunctionIR]:
    ir_gen = IRGenerator(ast)
    function_irs = ir_gen.generate()

    cfg_builder = CFGBuilder()
    optimizer = IROptimizer()

    for func_name, func_ir in function_irs.items():
        func_ir.basic_blocks = cfg_builder.build(func_ir)
        if do_optimize:
            opt_insts, opt_blocks = optimizer.optimize(func_ir)
            func_ir.optimized_instructions = opt_insts
            func_ir.optimized_basic_blocks = opt_blocks

    return function_irs


def main():
    parser = argparse.ArgumentParser(
        description="MiniCC - A simple compiler frontend CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Commands:
  lex SOURCE.mc       Run lexer and print token table
  parse SOURCE.mc     Run parser and print AST
  check SOURCE.mc     Run full pipeline (lexer+parser+type check) and print errors/symbol table
  ast SOURCE.mc       Run full pipeline and print typed AST (--json for JSON format)
  ir SOURCE.mc        Generate 3-address IR and CFG after type checking
                      Options: --json for JSON output, --opt to enable optimizations""")
    parser.add_argument('command', choices=['lex', 'parse', 'check', 'ast', 'ir'],
                        help='Command to execute')
    parser.add_argument('source', help='Source file path')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--opt', action='store_true', help='Enable IR optimizations')

    args = parser.parse_args()

    try:
        with open(args.source, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{args.source}' not found.", file=sys.stderr)
        sys.exit(1)

    lexer = Lexer(source, args.source)
    tokens, lexer_errors = lexer.tokenize()

    if args.command == 'lex':
        print("=" * 60)
        print("Token Stream")
        print("=" * 60)
        print(format_token_table(tokens))
        if lexer_errors:
            print()
            print(format_errors(lexer_errors, "Lexer Errors"))
        sys.exit(1 if lexer_errors else 0)

    if lexer_errors:
        print(format_errors(lexer_errors, "Lexer Errors"))
        print("\nCannot proceed to parsing due to lexer errors.", file=sys.stderr)
        sys.exit(1)

    p = Parser(tokens)
    ast, parse_errors = p.parse()

    if args.command == 'parse':
        print("=" * 60)
        print("Abstract Syntax Tree")
        print("=" * 60)
        print(format_ast_tree(ast))
        if parse_errors:
            print()
            print(format_errors(parse_errors, "Parse Errors"))
        sys.exit(1 if parse_errors else 0)

    checker = TypeChecker(ast)
    type_errors = checker.check()

    all_errors = []
    for pe in parse_errors:
        all_errors.append(TypeCheckError(pe.message, pe.line, pe.col, "error"))
    all_errors.extend(type_errors)
    has_errors = any(e.severity == "error" for e in all_errors)
    has_warnings = any(e.severity == "warning" for e in all_errors)

    if args.command == 'check':
        print("=" * 60)
        print("Type Check & Symbol Table")
        print("=" * 60)
        errors_only = [e for e in all_errors if e.severity == "error"]
        warnings = [e for e in all_errors if e.severity == "warning"]
        if errors_only:
            print(format_errors(errors_only, "Errors"))
        if warnings:
            print(format_errors(warnings, "Warnings"))
        if not errors_only and not warnings:
            print("No errors or warnings.")
        print()
        print(format_symbol_table(checker))
        sys.exit(1 if errors_only else 0)

    if args.command == 'ast':
        if args.json:
            diagnostics = []
            for e in all_errors:
                diagnostics.append({
                    "severity": e.severity,
                    "message": e.message,
                    "line": e.line,
                    "col": e.col,
                })
            output = {
                "ast": ast.to_dict(),
                "diagnostics": diagnostics,
                "has_errors": has_errors,
                "has_warnings": has_warnings,
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print("=" * 60)
            print("Typed Abstract Syntax Tree")
            print("=" * 60)
            print(format_ast_tree(ast))
            if all_errors:
                print()
                print(format_errors(all_errors, "Diagnostics"))
        sys.exit(1 if has_errors else 0)

    if args.command == 'ir':
        diagnostics = []
        for e in all_errors:
            diagnostics.append({
                "severity": e.severity,
                "message": e.message,
                "line": e.line,
                "col": e.col,
            })

        if has_errors:
            if args.json:
                output = {
                    "diagnostics": diagnostics,
                    "has_errors": True,
                    "has_warnings": has_warnings,
                    "functions": {},
                }
                print(json.dumps(output, indent=2, ensure_ascii=False))
            else:
                print("=" * 60)
                print("IR Generation Failed")
                print("=" * 60)
                print(format_errors(all_errors, "Diagnostics"))
                print("\nCannot generate IR due to errors above.")
            sys.exit(1)

        function_irs = build_ir_with_cfg(ast, do_optimize=args.opt)

        if args.json:
            functions_dict = {}
            for fname, fir in function_irs.items():
                if args.opt:
                    functions_dict[fname] = fir.to_dict(compare=True)
                else:
                    functions_dict[fname] = fir.to_dict(optimized=False)
            output = {
                "diagnostics": diagnostics,
                "has_errors": False,
                "has_warnings": has_warnings,
                "functions": functions_dict,
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            if has_warnings:
                warnings = [e for e in all_errors if e.severity == "warning"]
                print(format_errors(warnings, "Warnings"))
                print()

            if args.opt:
                print("=" * 80)
                print("IR Optimization: Before vs After Comparison")
                print("=" * 80)
                print()
                print(format_ir_compare(function_irs))
                print("=" * 80)
                print("Optimization Summary")
                print("=" * 80)
                total_orig = 0
                total_opt = 0
                for fname, fir in function_irs.items():
                    orig_count = len(fir.instructions)
                    opt_count = len(fir.optimized_instructions) if fir.optimized_instructions else orig_count
                    total_orig += orig_count
                    total_opt += opt_count
                    print(f"  {fname:30s} {orig_count:4d} -> {opt_count:4d} instructions  (removed {orig_count - opt_count:3d}, {int((orig_count-opt_count)/orig_count*100) if orig_count > 0 else 0}%)")
                print(f"  {'TOTAL':30s} {total_orig:4d} -> {total_opt:4d} instructions  (removed {total_orig - total_opt:3d}, {int((total_orig-total_opt)/total_orig*100) if total_orig > 0 else 0}%)")
            else:
                print("=" * 60)
                print("Intermediate Representation (IR) and Control Flow Graph")
                print("=" * 60)
                print(format_ir(function_irs, optimized=False))
        sys.exit(0)


if __name__ == '__main__':
    main()
