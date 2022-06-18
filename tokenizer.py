"""Token Generator for simple BASIC-like language.
For use in my personal studies of compilers
06/13/2022"""
import re
from typing import AnyStr, Union

from regex import Pattern
from typing_extensions import Self

from tokens import TOKEN_TYPES, TokenType


class Token:
    """Language Tokens"""

    def __init__(self, tokenText: str, tokenKind: TokenType) -> None:

        self.text: str = tokenText
        self.kind: TokenType = tokenKind

    @staticmethod
    def check_if_keyword(token_text: str) -> Union[TokenType, None]:
        """Check if a string is a keyword token. Return token kind if successful

        Args:
            token_text (str): string to check

        Returns:
            Union[TokenType,None]: TokenType kind for use in constructing keyword token
        """
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == token_text and kind.value >= 100 and kind.value < 200:
                return kind


class TokenGenerator:
    """Takes a string and outputs a generator of Tokens

    Example:

    print(list(token.kind for token in TokenGenerator('+-*')))

    User> [<TokenType.PLUS: 202>,<TokenType.MINUS: 203>,<TokenType.STAR: 204>]
    """

    def __init__(self, input: str) -> None:
        input: str = self._remove_whitespace(input)
        self._source: str = self._remove_comments(input)
        self._cur_pos: int = 0
        self._next_char: str = ""
        self._at_end: bool = False

    def _peek(self) -> str:
        """Returns next char in source string or EOF

        Returns:
            str: next char in source string
        """

        try:
            return self._source[self._cur_pos + 1]
        except IndexError:
            return "\0"

    def _remove_whitespace(self, input: str) -> str:
        """Remove whitespace except for newlines from input string

        Args:
            input (str): input string

        Returns:
            str: input string after removeing all whitespace except newlines
        """

        regex: Pattern[AnyStr @ compile] = re.compile(r'"[^"]*"|([^\S\r\n]+)')

        return regex.sub(lambda x: "" if x.group(1) else x.group(0), input)

    def _remove_comments(self, input: str) -> str:
        """Remove comments (anything between /* and */) from input string

        Args:
            input (str): input string

        Returns:
            str: string sans comments
        """

        return re.sub(r"\/\*.*\*\/", "", input)

    def _get_number(self, cur_char: str) -> Union[Token, None]:
        """Return number token if input char is a digit, else None

        Args:
            cur_char (str): input char

        Returns:
            Union[Token,None]: Number token or None
        """
        if cur_char.isdigit():
            # Leading character is a digit, so this must be a number.
            # Get all consecutive digits and decimal if there is one.
            start_pos: int = self._cur_pos
            while self._peek().isdigit():
                self._cur_pos += 1
            if self._peek() == ".":
                self._cur_pos += 1
                # Must have at least one digit after decimal.
                if not self._peek().isdigit():
                    raise ValueError("Illegal character in number!")
                while self._peek().isdigit():
                    self._cur_pos += 1

            tok_text: str = self._source[start_pos: self._cur_pos + 1]
            return Token(tok_text, TokenType.NUMBER)

    def _get_ident_or_keyword(self, cur_char: str) -> Union[Token, None]:
        """Returns IDENT or keyword token if input char is alpha, else None

        Args:
            cur_char (str): input char

        Returns:
            Union[Token,None]: IDENT/Keyword token or None
        """
        if cur_char.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword.
            # Get all consecutive alphanumeric characters.
            start_pos: int = self._cur_pos
            while self._peek().isalnum():
                self._cur_pos += 1

            # Check if the token is in the list of keywords.
            tok_text: str = self._source[start_pos: self._cur_pos + 1]
            if keyword := Token.check_if_keyword(tok_text):
                token: Token = Token(tok_text, keyword)
            else:
                token: Token = Token(tok_text, TokenType.IDENT)
            return token

    def _get_string(self, cur_char: str) -> Union[Token, None]:
        """Returns STRING token if input char is an escaped double quote, else None

        Args:
            cur_char (str): input char

        Returns:
            Union[Token,None]: STRING token or None
        """
        if cur_char == '"':
            string_end: int = self._source.find('"', self._cur_pos + 1)
            string_token: str = self._source[self._cur_pos + 1: string_end]
            self._cur_pos += len(string_token) + 1
            return Token(string_token, TokenType.STRING)

    def _get_EOF(self, cur_char: str) -> Union[Token, None]:
        """Returns EOF char if input char is ascii null, else None

        Args:
            cur_char (str): input char

        Returns:
            Union[Token, None]: EOF token or None
        """
        if cur_char == "\0":
            return Token(cur_char, TokenType.EOF)

    def _get_newlines(self, cur_char: str) -> Union[Token, None]:
        """Returns NEWLINE token if input char is newline, else None

        Args:
            cur_char (str): input char

        Returns:
            Union[Token,None]: NEWLINE token or None
        """
        if cur_char in ["\n", "\r\n"]:
            return Token(cur_char, TokenType.NEWLINE)

    def _is_operator(self, cur_char: str) -> Union[Token, None]:
        """Returns the operator token corresponding to the input char, else None

        Args:
            cur_char (str): input char

        Returns:
            Union[Token,None]: Operator token or None
        """
        try:
            token_type: TokenType = TOKEN_TYPES[cur_char + self._peek()]
            second_char: str = self._peek()
            self._cur_pos += 1
            return Token(cur_char + second_char, token_type)
        except KeyError:
            try:
                token_type: TokenType = TOKEN_TYPES[cur_char]
                return Token(cur_char, token_type)
            except KeyError:
                return None

    def _get_next_token(self, cur_char: str) -> Token:
        """Return the next token in the source string to the __next__ method

        Args:
            cur_char (str): current char in source string

        Returns:
            Token: Next token in source string
        """

        lexing_strats = [
            self._get_number,
            self._get_ident_or_keyword,
            self._get_EOF,
            self._get_newlines,
            self._get_string,
            self._is_operator,
        ]
        for strat in lexing_strats:
            if token := strat(cur_char):
                return token
        else:
            raise ValueError(f"Lexing Error! Character '{cur_char}' not recognized")

    def __next__(self) -> Token:

        if self._at_end:
            raise StopIteration

        # set flag true to raise StopIteration on next pass after getting EOF Token
        if self._next_char == "\0":
            self._at_end: bool = True

        # Get next char. If no more chars, set cur_char to null char
        try:
            cur_char: str = self._source[self._cur_pos]
        except IndexError:
            cur_char: str = "\0"
        token: Token = self._get_next_token(cur_char)
        self._next_char: str = self._peek()
        self._cur_pos += 1
        return token

    def __iter__(self) -> Self:

        return self


def main() -> None:

    input_string: str = """+ * -567.98 /=<>\"blah\"<=> == =!=/*comments*/
    + *- /=\"this is a string\"<>IF<=> =
    <=> == =!=
    =
    LABEL
    GOTO
    PRINT
    INPUT
    LET
    IF
    THEN
    ENDIF
    WHILE
    REPEAT
    ENDWHILE
    """

    tokengen: TokenGenerator = TokenGenerator(input_string)
    print(list(token.text for token in tokengen))


if __name__ == "__main__":
    main()
