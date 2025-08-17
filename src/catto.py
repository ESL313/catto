from dataclasses import dataclass
from enum import Enum, auto
from re import findall
from sys import argv
from typing import Callable


Token = tuple[str, str, str]


class WordType(Enum):
    STRING = auto()  # foo
    DEFINE = auto()  # :bar
    CALL = auto()  # $baz


@dataclass
class Word:
    type: WordType
    value: str


class Stack:

    value: list[str]

    def __init__(self):
        self.value = []

    def push(self, item: str):
        self.value.append(item)

    def pop(self) -> str:
        if len(self.value) <= 0:
            return ""
        else:
            return self.value.pop()


# These are for builtin words, e.g., drop, swap, etc.
builtins: dict[str, Callable[[Stack], None]] = {}
# These are for user-defined words.
dictionary: dict[str, list[Word]] = {}


def lexLines(lines: list[str]) -> list[Token]:
    result: list[Token] = []
    for line in lines:
        # Has three capture groups: the first represents the word type,
        # the second and third are mutually exclusive and represent the string value.
        tokens: list[Token] = findall(r'([:$]?)(?:([^ \t\r"]+)|"((?:[^"\\]*(?:\\.)?)*)")', line)
        for token in tokens:
            result.append(token)
    return result


def lexString(string: str) -> list[Token]:
    return lexLines(string.split("\n"))


def parseTokens(tokens: list[Token]) -> list[Word]:
    result: list[Word] = []
    for token in tokens:
        wordType, shortString, longString = token
        value: str
        if shortString == "":
            # Uses Python's escape sequence parser.
            value = bytes(longString, "utf-8").decode("unicode_escape")
        else:
            value = shortString

        match wordType:
            case "":
                result.append(Word(WordType.STRING, value))
            case ":":
                result.append(Word(WordType.DEFINE, value))
            case "$":
                result.append(Word(WordType.CALL, value))
            case _:
                # This should be unreachable.
                raise NotImplementedError("Invalid WordType.")

    return result


def evaluateWords(words: list[Word], stack: Stack):
    while len(words) > 0:
        word: Word = words[0]
        words = words[1:]
        match word.type:
            case WordType.STRING:
                stack.push(word.value)
            case WordType.DEFINE:
                dictionary[word.value] = parseTokens(lexString(stack.pop()))
            case WordType.CALL:
                if word.value in builtins:
                    builtins[word.value](stack)
                elif word.value in dictionary:
                    words = dictionary[word.value] + words
                else:
                    pass  # Undefined words do nothing when called.


def main():
    # Read every line until EOF.
    lines: list[str] = []
    while True:
        try:
            line: str = input()
        except EOFError:
            break
        lines.append(line)

    # Use argv contents as the initial stack.
    stack: Stack = Stack()
    for argument in argv[1:]:
        stack.push(argument)

    try:
        evaluateWords(parseTokens(lexLines(lines)), stack)
    except RecursionError:
        # Is it really an error if a program is valid while taking infinite time to complete...?
        print("Recursion Limit :(")
    else:
        # Output the whole stack once everything is done.
        for item in stack.value:
            print(item)


### Start of Helper Functions for Builtins ###


def addBuiltin(name: str):
    def decorator(func: Callable[[Stack], None]):
        builtins[name] = func

    return decorator


def createRotBuiltin(n: int):
    def builtinRot(stack: Stack):
        values: list[str] = [stack.pop() for _ in range(n)]
        values = [values[-1]] + values[:-1]
        [stack.push(item) for item in values[::-1]]

    return builtinRot


def createUnaryOpBuiltin(func: Callable[[str], str]):
    def builtinUnaryOp(stack: Stack):
        item: str = stack.pop()
        result: str
        try:
            result = func(item)
        except:
            result = "Undefined"
        stack.push(result)

    return builtinUnaryOp


def createBinaryOpBuiltin(func: Callable[[str, str], str]):
    def builtinBinaryOp(stack: Stack):
        a: str = stack.pop()
        b: str = stack.pop()
        result: str
        try:
            result = func(b, a)
        except:
            result = "Undefined"
        stack.push(result)

    return builtinBinaryOp


def createTrinaryOpBuiltin(func: Callable[[str, str, str], str]):
    def builtinTrinaryOp(stack: Stack):
        a: str = stack.pop()
        b: str = stack.pop()
        c: str = stack.pop()
        result: str
        try:
            result = func(c, b, a)
        except:
            result = "Undefined"
        stack.push(result)

    return builtinTrinaryOp


def str2bool(string: str) -> bool:
    if string == "True":
        return True
    elif string == "False":
        return False
    else:
        # Should be catched by a try-clause.
        raise TypeError("Expected 'True' or 'False'.")


# Use this instead of 'int()' as 'int(1.0)' fails.
def str2int(string: str) -> int:
    return int(float(string))


# Use this for arithmetic operations so that operations with ints result in an int.
def str2num(string: str) -> int | float:
    result: int | float
    try:
        result = int(string)
    except:
        result = float(string)
    return result


### End of Helper Functions for Builtins ###
### Start of Builtin Words ###


@addBuiltin("drop")
def builtinDrop(stack: Stack):
    stack.pop()


@addBuiltin("dupe")
def builtinDupe(stack: Stack):
    item: str = stack.pop()
    stack.push(item)
    stack.push(item)


@addBuiltin("swap")
def builtinSwap(stack: Stack):
    a: str = stack.pop()
    b: str = stack.pop()
    stack.push(a)
    stack.push(b)


for i in range(3, 10):
    addBuiltin(f"rot{i}")(createRotBuiltin(i))

addBuiltin("+")(createBinaryOpBuiltin(lambda a, b: str(str2num(a) + str2num(b))))
addBuiltin("-")(createBinaryOpBuiltin(lambda a, b: str(str2num(a) - str2num(b))))
addBuiltin("*")(createBinaryOpBuiltin(lambda a, b: str(str2num(a) * str2num(b))))
addBuiltin("/")(createBinaryOpBuiltin(lambda a, b: str(str2num(a) / str2num(b))))
addBuiltin("~")(createUnaryOpBuiltin(lambda x: str(-str2num(x))))

# Use 'all()' and 'any()' instead of 'and' and 'or' to prevent short-circuit behaviour.
addBuiltin("and")(createBinaryOpBuiltin(lambda a, b: str(all([str2bool(a), str2bool(b)]))))
addBuiltin("or")(createBinaryOpBuiltin(lambda a, b: str(any([str2bool(a), str2bool(b)]))))
addBuiltin("not")(createUnaryOpBuiltin(lambda x: str(not str2bool(x))))

addBuiltin("==")(createBinaryOpBuiltin(lambda a, b: str(a == b)))
addBuiltin("!=")(createBinaryOpBuiltin(lambda a, b: str(a != b)))

addBuiltin("<")(createBinaryOpBuiltin(lambda a, b: str(str2num(a) < str2num(b))))
addBuiltin(">")(createBinaryOpBuiltin(lambda a, b: str(str2num(a) > str2num(b))))
addBuiltin("<=")(createBinaryOpBuiltin(lambda a, b: str(str2num(a) <= str2num(b))))
addBuiltin(">=")(createBinaryOpBuiltin(lambda a, b: str(str2num(a) >= str2num(b))))

addBuiltin("if")(
    createTrinaryOpBuiltin(
        lambda condition, trueString, falseString: trueString if str2bool(condition) else falseString
    )
)

addBuiltin("len")(createUnaryOpBuiltin(lambda x: str(len(x))))
addBuiltin("cat")(createBinaryOpBuiltin(lambda a, b: a + b))
addBuiltin("substr")(createTrinaryOpBuiltin(lambda string, start, end: string[str2int(start) : str2int(end)]))
addBuiltin("replace")(createTrinaryOpBuiltin(lambda string, old, new: string.replace(old, new)))

addBuiltin("int")(createUnaryOpBuiltin(lambda x: str(str2int(x))))
addBuiltin("float")(createUnaryOpBuiltin(lambda x: str(float(x))))


@addBuiltin("eval")
def builtinEval(stack: Stack):
    item: str = stack.pop()
    evaluateWords(parseTokens(lexString(item)), stack)


### End of Builtin Words ###

if __name__ == "__main__":
    main()
