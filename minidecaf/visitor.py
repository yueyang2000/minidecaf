from .generated.MiniDecafVisitor import MiniDecafVisitor
from .generated.MiniDecafParser import MiniDecafParser
from antlr4 import *
from .type_zoo import *


def Err(msg):
    raise Exception(msg)


class MainVisitor(MiniDecafVisitor):
    def __init__(self):
        self.asm = ''
        self.currentFunc = ''
        self.containsMain = False

    def push(self, reg):
        self.asm += '# push ' + reg + "\n"
        self.asm += '\taddi sp, sp, -4\n'
        self.asm += '\tsw ' + reg + ', 0(sp)\n'

    def pop(self, reg):
        self.asm += '# pop ' + reg + '\n'
        self.asm += '\tlw ' + reg + ', 0(sp)\n'
        self.asm += '\t addi sp, sp, 4\n'
    # Visit a parse tree produced by MiniDecafParser#prog.

    def visitProg(self, ctx: MiniDecafParser.ProgContext):
        self.visit(ctx.func())
        if not self.containsMain:
            Err("no main function")
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#func.
    def visitFunc(self, ctx: MiniDecafParser.FuncContext):
        self.currentFunc = ctx.IDENT().getText()
        if self.currentFunc == "main":
            self.containsMain = True
        self.asm += '\t.text\n\t.global ' + \
            self.currentFunc + '\n' + self.currentFunc + ":\n"
        self.visit(ctx.stmt())
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#ty.
    def visitTy(self, ctx: MiniDecafParser.TyContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by MiniDecafParser#stmt.
    def visitStmt(self, ctx: MiniDecafParser.StmtContext):
        self.visit(ctx.expr())
        self.pop('a0')
        self.asm += '\tret\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#expr.
    def visitExpr(self, ctx: MiniDecafParser.ExprContext):
        return self.visit(ctx.lor())

    # Visit a parse tree produced by MiniDecafParser#lor.
    def visitLor(self, ctx: MiniDecafParser.LorContext):
        if len(ctx.children) > 1:
            self.visit(ctx.lor(0))
            self.visit(ctx.lor(1))
            self.pop('t1')
            self.pop('t0')
            self.asm += '\tsnez t0, t0\n'
            self.asm += '\tsnez t1, t1\n'
            self.asm += '\tor t0, t0, t1\n'
            self.push('t0')
            return IntType()
        else:
            return self.visit(ctx.land())

    # Visit a parse tree produced by MiniDecafParser#land.
    def visitLand(self, ctx: MiniDecafParser.LandContext):
        if len(ctx.children) > 1:
            self.visit(ctx.land(0))
            self.visit(ctx.land(1))
            self.pop('t1')
            self.pop('t0')
            self.asm += '\tsnez t0, t0\n'
            self.asm += '\tsnez t1, t1\n'
            self.asm += '\tand t0, t0, t1\n'
            self.push('t0')
            return IntType()
        else:
            return self.visit(ctx.equ())

    # Visit a parse tree produced by MiniDecafParser#equ.
    def visitEqu(self, ctx: MiniDecafParser.EquContext):
        if len(ctx.children) > 1:
            self.visit(ctx.equ(0))
            self.visit(ctx.equ(1))
            self.pop('t1')
            self.pop('t0')
            op = ctx.children[1].getText()
            if op == '==':
                self.asm += '\tsub t0, t0, t1\n'
                self.asm += '\tseqz t0, t0\n'
            elif op == '!=':
                self.asm += '\tsub t0, t0, t1\n'
                self.asm += '\tsnez t0, t0\n'
            else:
                Err('illigal operator ' + op)
            self.push('t0')
            return IntType()
        else:
            return self.visit(ctx.rel())

    # Visit a parse tree produced by MiniDecafParser#rel.
    def visitRel(self, ctx: MiniDecafParser.RelContext):
        if len(ctx.children) > 1:
            self.visit(ctx.rel(0))
            self.visit(ctx.rel(1))
            self.pop('t1')
            self.pop('t0')
            op = ctx.children[1].getText()
            if op == '<':
                self.asm += '\tslt t0, t0, t1\n'
            elif op == '<=':
                self.asm += '\tsgt t0, t0, t1\n'
                self.asm += '\txori t0, t0, 1\n'
            elif op == '>':
                self.asm += '\tsgt t0, t0, t1\n'
            elif op == '>=':
                self.asm += '\tslt t0, t0, t1\n'
                self.asm += '\txori t0, t0, 1\n'
            else:
                Err('illigal operator ' + op)
            self.push('t0')
            return IntType()
        else:
            return self.visit(ctx.add())

    # Visit a parse tree produced by MiniDecafParser#add.
    def visitAdd(self, ctx: MiniDecafParser.AddContext):
        if len(ctx.children) > 1:
            self.visit(ctx.add(0))
            self.visit(ctx.add(1))
            self.pop('t1')
            self.pop('t0')
            op = ctx.children[1].getText()
            if op == '+':
                self.asm += '\tadd t0, t0, t1\n'
            elif op == '-':
                self.asm += '\tsub t0, t0, t1\n'
            else:
                Err('illigal operator ' + op)
            self.push('t0')
            return IntType()
        else:
            self.visit(ctx.mul())

    # Visit a parse tree produced by MiniDecafParser#mul.
    def visitMul(self, ctx: MiniDecafParser.MulContext):
        if len(ctx.children) > 1:
            self.visit(ctx.mul(0))
            self.visit(ctx.mul(1))

            self.pop('t1')
            self.pop('t0')
            op = ctx.children[1].getText()
            if op == '*':
                self.asm += '\tmul t0, t0, t1\n'
            elif op == '/':
                self.asm += '\tdiv t0, t0, t1\n'
            elif op == '%':
                self.asm += '\trem t0, t0, t1\n'
            else:
                Err('illigal operator ' + op)
            self.push('t0')
            return IntType()
        else:
            return self.visit(ctx.unary())

    # Visit a parse tree produced by MiniDecafParser#unary.
    def visitUnary(self, ctx: MiniDecafParser.UnaryContext):
        if len(ctx.children) > 1:
            self.visit(ctx.unary())
            op = ctx.children[0].getText()
            self.pop('t0')
            if op == '-':
                self.asm += '\tneg t0, t0\n'
            elif op == '!':
                self.asm += '\tseqz t0, t0\n'
            elif op == '~':
                self.asm += '\tnot t0, t0\n'
            else:
                Err('illigal operator ' + op)
            self.push('t0')
            return IntType()
        else:
            return self.visit(ctx.primary())

    # Visit a parse tree produced by MiniDecafParser#numPrimary.
    def visitNumPrimary(self, ctx: MiniDecafParser.NumPrimaryContext):
        num = ctx.NUM()
        num_text = num.getText()
        if int(num_text) >= 2147483648:
            Err('too large number')
        self.asm += '\tli t0, ' + num_text + '\n'
        self.push('t0')
        return IntType()

    # Visit a parse tree produced by MiniDecafParser#parenthesizedPrimary.
    def visitParenthesizedPrimary(self, ctx: MiniDecafParser.ParenthesizedPrimaryContext):
        return self.visit(ctx.expr())
