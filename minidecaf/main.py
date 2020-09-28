from .generated.MiniDecafParser import MiniDecafParser
from .generated.MiniDecafVisitor import MiniDecafVisitor
from .generated.MiniDecafLexer import MiniDecafLexer
from antlr4 import *
from .visitor import MainVisitor
import sys


def main(argv):
    try:
        infile = argv[1]
        inputStream = FileStream(infile)
        lexer = MiniDecafLexer(inputStream)
        tokenStream = CommonTokenStream(lexer)

        parser = MiniDecafParser(tokenStream)
        parser._errHandler = BailErrorStrategy()
        tree = parser.prog()
        visitor = MainVisitor()
        visitor.visit(tree)
        asm = visitor.asm
        print(asm)
        return 0
    except Exception as e:
        raise e
        print(e, file=sys.stderr)
        return 1
