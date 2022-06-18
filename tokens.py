from enum import Enum


class TokenType(Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER =1
    IDENT = 2
    STRING = 3
    # Keywords
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    #Operators
    EQ = 201
    PLUS = 202
    MINUS = 203
    STAR = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


TOKEN_TYPES: dict[str, TokenType] = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.STAR,
    "/": TokenType.SLASH,
    "<": TokenType.LT,
    ">": TokenType.GT,
    "<=": TokenType.LTEQ,
    ">=": TokenType.GTEQ,
    "=": TokenType.EQ,
    "==": TokenType.EQEQ,
    "!=": TokenType.NOTEQ,
}
