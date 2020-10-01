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
        self.condNo = 0
        self.loopNo = 0
        self.loopNos = []
        self.localCnt = 0
        self.symbolTable = []

        self.declaredGlobalTable = {}
        self.initializedGlobalTable = {}

        self.declaredFuncTable = {}
        self.definedFuncTable = {}

    def push(self, reg):
        self.asm += '#push ' + reg + '\n\taddi sp, sp, -4\n'
        self.asm += '\tsw ' + reg + ', 0(sp)\n\n'

    def pop(self, reg):
        self.asm += '#pop ' + reg + '\n\tlw ' + reg + ', 0(sp)\n'
        self.asm += '\taddi sp, sp, 4\n\n'

    def getSymbol(self, name):
        for i in range(len(self.symbolTable) - 1, -1, -1):
            table = self.symbolTable[i]
            if name in table:
                return table[name]
        return None

    def RCast(self, Type):
        if Type.rvalue == False:
            self.pop('t0')
            self.asm += '\tlw t0, 0(t0)\n'
            self.push('t0')
        return Type.valueCast(True)

    # Visit a parse tree produced by MiniDecafParser#prog.

    def visitProg(self, ctx: MiniDecafParser.ProgContext):
        for child in ctx.children:
            self.visit(child)
        for glob in self.declaredGlobalTable:
            if not glob in self.initializedGlobalTable:
                self.asm = '\t.comm ' + glob + ',' + \
                    str(self.declaredGlobalTable[glob].getSize(
                    )) + ',4\n\n' + self.asm
        if not self.containsMain:
            Err("no main function")
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#definedFunc.
    def visitDefinedFunc(self, ctx: MiniDecafParser.DefinedFuncContext):
        self.currentFunc = ctx.IDENT(0).getText()
        if self.currentFunc in self.declaredGlobalTable:
            Err('global name confliction')
        if self.currentFunc == "main":
            self.containsMain = True
        self.asm += '\t.text\n\t.global ' + \
            self.currentFunc + '\n'
        self.asm += self.currentFunc + ":\n"
        if self.currentFunc in self.definedFuncTable:
            Err("defined two function with the same name")
        rtnType = self.visit(ctx.ty(0))
        paramTypes = []
        for i in range(1, len(ctx.ty())):
            paramTypes.append(self.visit(ctx.ty(i)))
        funType = FunType(rtnType, paramTypes)

        if self.currentFunc in self.declaredFuncTable:
            declaredType = self.declaredFuncTable[self.currentFunc]
            if not declaredType == funType:
                Err("function type mismatch")

        self.declaredFuncTable[self.currentFunc] = funType
        self.definedFuncTable[self.currentFunc] = funType

        self.push('ra')
        self.push('fp')
        self.asm += '\tmv fp, sp\n'
        backPos = len(self.asm)
        self.localCnt = 0

        field = {}
        for i in range(1, len(ctx.IDENT())):
            paramName = ctx.IDENT(i).getText()
            if paramName in field:
                Err('two param has the same name')
            if i < 9:
                self.localCnt += 1
                self.asm += '\tsw a' + \
                    str(i - 1) + ', ' + str(-4 * i) + '(fp)\n'
                field[paramName] = Symbol(
                    paramName, -4 * i, funType.paramTypes[i - 1].valueCast(False))
            else:
                field[paramName] = Symbol(
                    paramName, 4 * (i - 9 + 2), funType.paramTypes[i - 1].valueCast(False))

        self.symbolTable.append(field)

        for block in ctx.blockItem():
            self.visit(block)

        self.symbolTable.pop()
        self.asm += '\tli t1, 0\n'
        self.asm += '\taddi sp, sp, -4\n'
        self.asm += '\tsw t1, 0(sp)\n'

        stack_space = "\taddi sp, sp, " + str(-4 * self.localCnt) + "\n"
        tmp = list(self.asm)
        tmp.insert(backPos, stack_space)
        self.asm = ''.join(tmp)

        self.asm += '.exit.' + self.currentFunc + ':\n'
        self.asm += '\tlw a0, 0(sp)\n'
        self.asm += '\tmv sp, fp\n'
        self.pop('fp')
        self.pop('ra')
        self.asm += '\tret\n'

        return NoType()

    # Visit a parse tree produced by MiniDecafParser#declaredFunc.
    def visitDeclaredFunc(self, ctx: MiniDecafParser.DeclaredFuncContext):
        funcName = ctx.IDENT(0).getText()
        if funcName in self.declaredGlobalTable:
            Err("symbol confliction")
        rtnType = self.visit(ctx.ty(0))
        paramTypes = []
        for i in range(1, len(ctx.ty())):
            paramTypes.append(self.visit(ctx.ty(i)))
        funType = FunType(rtnType, paramTypes)
        if funcName in self.declaredFuncTable:
            declaredType = self.declaredFuncTable[funcName]
            if not declaredType == funType:
                Err('declare a function with two different type', ctx)
        self.declaredFuncTable[funcName] = funType
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#ty.
    def visitTy(self, ctx: MiniDecafParser.TyContext):
        starNum = len(ctx.children) - 1
        if starNum == 0:
            return IntType()
        else:
            return PointerType(starNum)

    # Visit a parse tree produced by MiniDecafParser#globalIntOrPointerDecl.
    def visitGlobalIntOrPointerDecl(self, ctx: MiniDecafParser.GlobalIntOrPointerDeclContext):
        name = ctx.IDENT().getText()
        if name in self.declaredFuncTable:
            Err("symbol confliction")
        Type = self.visit(ctx.ty())
        if name in self.declaredGlobalTable and not(self.declaredGlobalTable[name] == Type):
            Err("global variable type mismatch", ctx)
        self.declaredGlobalTable[name] = Type.valueCast(False)
        num = ctx.NUM()
        if num is not None:
            if name in self.initializedGlobalTable:
                Err("init global variable twice")
            self.initializedGlobalTable[name] = Type.valueCast(True)
            self.asm += '\t.data\n\t.global ' + name + '\n\t.align 4\n'
            self.asm += '\t.size ' + name + ', ' + str(Type.getSize()) + '\n'
            self.asm += name + ":\n" + '\t.quad ' + num.getText() + '\n\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#globalArrayDecl.
    def visitGlobalArrayDecl(self, ctx: MiniDecafParser.GlobalArrayDeclContext):
        name = ctx.IDENT().getText()
        if name in self.declaredFuncTable:
            Err('symbol confliction')
        types = []
        types.append(self.visit(ctx.ty()).valueCast(False))
        for i in range(len(ctx.NUM()) - 1, -1, -1):
            x = int(ctx.NUM(i).getText())
            if x >= 2147483648 or x < 0:
                Err('too large number')
            if x == 0:
                Err('dim of array cannot be 0')
            types.append(ArrayType(types[-1], x))
        Type = types[-1]
        if name in self.declaredGlobalTable and not self.declaredGlobalTable[name] == Type:
            Err('global variable conflict')
        self.declaredGlobalTable[name] = Type

        return NoType()

    # Visit a parse tree produced by MiniDecafParser#localIntOrPointerDecl.
    def visitLocalIntOrPointerDecl(self, ctx: MiniDecafParser.LocalIntOrPointerDeclContext):
        name = ctx.IDENT().getText()
        if name in self.symbolTable[-1]:
            Err('redeclare symbol')
        self.localCnt += 1
        Type = self.visit(ctx.ty())
        self.symbolTable[-1][name] = Symbol(name, -
                                            4 * self.localCnt, Type.valueCast(False))
        expr = ctx.expr()
        if expr is not None:
            exprType = self.RCast(self.visit(expr))
            if not exprType == Type:
                Err('type mismatch')
            self.pop('t0')
            self.asm += '\tsw t0, ' + str(-4 * self.localCnt) + '(fp)\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#localArrayDecl.
    def visitLocalArrayDecl(self, ctx: MiniDecafParser.LocalArrayDeclContext):
        name = ctx.IDENT().getText()
        if name in self.symbolTable[-1]:
            Err('redeclare local variable')
        types = []
        types.append(self.visit(ctx.ty()).valueCast(False))
        for i in range(len(ctx.NUM()) - 1, -1, -1):
            x = int(ctx.NUM(i).getText())
            if x == 0:
                Err('dim of array cannot be 0')
            types.append(ArrayType(types[-1], x))

        Type = types[-1]
        self.localCnt += int(Type.getSize() / 4)
        self.symbolTable[-1][name] = Symbol(name, -4 * self.localCnt, Type)
        return NoType()
    # Visit a parse tree produced by MiniDecafParser#exprStmt.

    def visitExprStmt(self, ctx: MiniDecafParser.ExprStmtContext):
        expr = ctx.expr()
        if expr is not None:
            self.visit(expr)
            self.pop('t0')
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#returnStmt.
    def visitReturnStmt(self, ctx: MiniDecafParser.ReturnStmtContext):
        rtnType = self.RCast(self.visit(ctx.expr()))
        expectedType = self.definedFuncTable[self.currentFunc].rtnType
        if not rtnType == expectedType:
            Err('return type mismatch')
        self.asm += '\tj .exit.' + self.currentFunc + '\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#ifStmt.
    def visitIfStmt(self, ctx: MiniDecafParser.IfStmtContext):
        currentCondNo = str(self.condNo)
        self.condNo += 1
        if self.RCast(self.visit(ctx.expr())).ty != 'INT':
            Err('expected int')
        self.pop('t0')
        self.asm += '\tbeqz t0, .else' + currentCondNo + '\n'
        self.visit(ctx.stmt(0))
        self.asm += '\tj .afterCond' + currentCondNo + '\n'
        self.asm += '.else' + currentCondNo + ':\n'
        if len(ctx.stmt()) > 1:
            self.visit(ctx.stmt(1))
        self.asm += '.afterCond' + currentCondNo + ':\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#blockStmt.
    def visitBlockStmt(self, ctx: MiniDecafParser.BlockStmtContext):
        self.symbolTable.append({})
        for block in ctx.blockItem():
            self.visit(block)
        self.symbolTable.pop()
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#whileStmt.
    def visitWhileStmt(self, ctx: MiniDecafParser.WhileStmtContext):
        currentLoopNo = str(self.loopNo)
        self.loopNo += 1
        self.asm += '.beforeLoop' + currentLoopNo + ':\n'
        self.asm += '.continueLoop' + currentLoopNo + ':\n'
        if self.RCast(self.visit(ctx.expr())).ty != 'INT':
            Err('expected int')
        self.pop('t0')
        self.asm += '\tbeqz t0, .afterLoop' + currentLoopNo + '\n'

        self.loopNos.append(currentLoopNo)
        self.visit(ctx.stmt())
        self.loopNos.pop()

        self.asm += '\tj .beforeLoop' + currentLoopNo + '\n'
        self.asm += '.afterLoop' + currentLoopNo + ':\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#forStmt.
    def visitForStmt(self, ctx: MiniDecafParser.ForStmtContext):
        currentLoopNo = str(self.loopNo)
        self.loopNo += 1

        initExpr = None
        condExpr = None
        afterExpr = None

        for i, expr in enumerate(ctx.children):
            if isinstance(expr, MiniDecafParser.ExprContext):
                if ctx.children[i - 1].getText() == '(':
                    initExpr = expr
                elif ctx.children[i + 1].getText() == ';':
                    condExpr = expr
                else:
                    afterExpr = expr
        self.symbolTable.append({})

        if initExpr is not None:
            self.visit(initExpr)
            self.asm += '\taddi sp, sp, 4\n'
        if ctx.localDecl() is not None:
            self.visit(ctx.localDecl())
        self.asm += '.beforeLoop' + currentLoopNo + ':\n'
        if condExpr is not None:
            if self.RCast(self.visit(condExpr)).ty != 'INT':
                Err('expected int')
            self.asm += '\tlw t1, 0(sp)\n'
            self.asm += '\taddi sp, sp, 4\n'
            self.asm += '\tbeqz t1, .afterLoop' + currentLoopNo + '\n'
        self.loopNos.append(currentLoopNo)
        self.symbolTable.append({})
        self.visit(ctx.stmt())
        self.symbolTable.pop()
        self.loopNos.pop()

        self.asm += '.continueLoop' + currentLoopNo + ':\n'
        if afterExpr is not None:
            self.visit(afterExpr)
            self.asm += '\taddi sp, sp, 4\n'
        self.symbolTable.pop()

        self.asm += '\tj .beforeLoop' + currentLoopNo + '\n'
        self.asm += '.afterLoop' + currentLoopNo + ':\n'
        return NoType()

        # Visit a parse tree produced by MiniDecafParser#doStmt.

    def visitDoStmt(self, ctx: MiniDecafParser.DoStmtContext):
        currentLoopNo = str(self.loopNo)
        self.loopNo += 1

        self.asm += '.beforeLoop' + currentLoopNo + ':\n'
        self.loopNos.append(currentLoopNo)
        self.visit(ctx.stmt())
        self.loopNos.pop()
        self.asm += '.continueLoop' + currentLoopNo + ':\n'
        if self.RCast(self.visit(ctx.expr())).ty != 'INT':
            Err('expected int')
        self.pop('t0')
        self.asm += '\tbnez t0, .beforeLoop' + currentLoopNo + '\n'
        self.asm += '.afterLoop' + currentLoopNo + ':\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#breakStmt.
    def visitBreakStmt(self, ctx: MiniDecafParser.BreakStmtContext):
        if len(self.loopNos) == 0:
            Err('break outside loop')
        self.asm += '\tj .afterLoop' + self.loopNos[-1] + '\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#continueStmt.
    def visitContinueStmt(self, ctx: MiniDecafParser.ContinueStmtContext):
        if len(self.loopNos) == 0:
            Err('continue outside loop')
        self.asm += '\t j .continueLoop' + self.loopNos[-1] + '\n'
        return NoType()

    # Visit a parse tree produced by MiniDecafParser#expr.
    def visitExpr(self, ctx: MiniDecafParser.ExprContext):
        if len(ctx.children) > 1:
            unaryType = self.visit(ctx.unary())
            if unaryType.rvalue:
                Err('needed lvalue')
            exprType = self.RCast(self.visit(ctx.expr()))
            if not exprType == unaryType.valueCast(True):
                Err('assign error')
            self.pop('t1')
            self.pop('t0')
            self.asm += '\tsw t1, 0(t0)'
            self.push('t0')
            return unaryType
        else:
            return self.visit(ctx.ternary())

    # Visit a parse tree produced by MiniDecafParser#ternary.
    def visitTernary(self, ctx: MiniDecafParser.TernaryContext):
        if len(ctx.children) > 1:
            currentCondNo = str(self.condNo)
            self.condNo += 1
            if self.RCast(self.visit(ctx.lor())).ty != 'INT':
                Err('expected int')

            self.pop('t0')
            self.asm += '\tbeqz t0, .else' + currentCondNo + '\n'
            thenType = self.RCast(self.visit(ctx.expr()))
            self.asm += 'j .afterCond' + currentCondNo + '\n'
            self.asm += '.else' + currentCondNo + ':\n'
            elseType = self.RCast(self.visit(ctx.ternary()))
            self.asm += '.afterCond' + currentCondNo + ':\n'
            if not thenType == elseType:
                Err('branch type mismatch')
            return IntType()
        else:
            return self.visit(ctx.lor())

    # Visit a parse tree produced by MiniDecafParser#lor.
    def visitLor(self, ctx: MiniDecafParser.LorContext):
        if len(ctx.children) > 1:
            if self.RCast(self.visit(ctx.lor(0))).ty != 'INT':
                Err('expected int')
            if self.RCast(self.visit(ctx.lor(1))).ty != 'INT':
                Err('expected int')
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
            if self.RCast(self.visit(ctx.land(0))).ty != 'INT':
                Err('expected int')
            if self.RCast(self.visit(ctx.land(1))).ty != 'INT':
                Err('expected int')
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
            leftType = self.RCast(self.visit(ctx.equ(0)))
            rightType = self.RCast(self.visit(ctx.equ(1)))
            if not leftType == rightType:
                Err('type mismatch')
            if leftType.ty == 'ARRAY' or rightType.ty == 'ARRAY':
                Err('array type cannot perform equ operation')
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
            if self.RCast(self.visit(ctx.rel(0))).ty != 'INT':
                Err('expected int')
            if self.RCast(self.visit(ctx.rel(1))).ty != 'INT':
                Err('expected int')
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
            leftType = self.RCast(self.visit(ctx.add(0)))
            rightType = self.RCast(self.visit(ctx.add(1)))
            op = ctx.children[1].getText()
            self.pop('t1')
            self.pop('t0')
            if op == '+':
                if leftType.ty == 'INT' and rightType.ty == 'INT':
                    self.asm += '\tadd t0, t0, t1\n'
                    self.push('t0')
                    return IntType()
                elif leftType.ty == 'POINTER' and rightType.ty == 'INT':
                    self.asm += '\tslli t1, t1, 2\n'
                    self.asm += '\tadd t0, t0, t1\n'
                    self.push('t0')
                    return leftType
                elif leftType.ty == 'INT' and rightType.ty == 'POINTER':
                    self.asm += '\tslli t0, t0, 2\n'
                    self.asm += '\tadd t0, t0, t1\n'
                    self.push('t0')
                    return rightType
                else:
                    Err('illigal ' + op)
            elif op == '-':
                if leftType.ty == 'INT' and rightType.ty == 'INT':
                    self.asm += '\tsub t0, t0, t1\n'
                    self.push('t0')
                    return IntType()
                elif leftType.ty == 'POINTER' and rightType.ty == 'INT':
                    self.asm += '\tslli t1, t1, 2\n'
                    self.asm += '\tsub t0, t0, t1\n'
                    self.push('t0')
                    return leftType
                elif leftType.ty == 'POINTER' and rightType == leftType:
                    self.asm += '\tsub t0, t0, t1\n'
                    self.asm += '\tsrai t0, t0, 2\n'
                    self.push('t0')
                    return IntType()
                else:
                    Err('illigal ' + op)
            else:
                Err('illigal operator ' + op)

        else:
            return self.visit(ctx.mul())

    # Visit a parse tree produced by MiniDecafParser#mul.
    def visitMul(self, ctx: MiniDecafParser.MulContext):
        if len(ctx.children) > 1:
            if self.RCast(self.visit(ctx.mul(0))).ty != 'INT':
                Err('expected int')
            if self.RCast(self.visit(ctx.mul(1))).ty != 'INT':
                Err('expected int')

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

    # Visit a parse tree produced by MiniDecafParser#opUnary.
    def visitOpUnary(self, ctx: MiniDecafParser.OpUnaryContext):
        Type = self.visit(ctx.unary())
        op = ctx.children[0].getText()
        if op == '*':
            return self.RCast(Type).dereferenced()
        elif op == '&':
            return Type.referenced()
        else:
            if self.RCast(Type).ty != 'INT':
                Err('expected int')
            self.pop('t0')
            if op == '-':
                self.asm += '\tneg t0, t0\n'
            elif op == '!':
                self.asm += '\tseqz t0, t0\n'
            elif op == '~':
                self.asm += '\tnot t0, t0\n'
            else:
                Err('illigal operator')
            self.push('t0')
            return IntType()

    # Visit a parse tree produced by MiniDecafParser#castUnary.
    def visitCastUnary(self, ctx: MiniDecafParser.CastUnaryContext):
        srcType = self.visit(ctx.unary())
        dstType = self.visit(ctx.ty())
        return dstType.valueCast(srcType.rvalue)

    # Visit a parse tree produced by MiniDecafParser#postfixUnary.
    def visitPostfixUnary(self, ctx: MiniDecafParser.PostfixUnaryContext):
        return self.visit(ctx.postfix())

    # Visit a parse tree produced by MiniDecafParser#subscriptPostfix.
    def visitSubscriptPostfix(self, ctx: MiniDecafParser.SubscriptPostfixContext):
        postfixType = self.RCast(self.visit(ctx.postfix()))
        if self.RCast(self.visit(ctx.expr())).ty != 'INT':
            Err('expected int')
        self.pop('t1')
        self.pop('t0')
        if postfixType.ty == 'POINTER':
            self.asm += '\tslli t1, t1, 2\n'
            self.asm += '\tadd t0, t0, t1\n'
            self.push('t0')
            return postfixType.dereferenced()
        elif postfixType.ty == 'ARRAY':
            baseType = postfixType.baseType
            self.asm += '\tli t2, ' + str(int(baseType.getSize())) + '\n'
            self.asm += '\tmul t1, t1, t2\n'
            self.asm += '\tadd t0, t0, t1'
            self.push('t0')
            return baseType
        else:
            Err('subscript unsupport')

    # Visit a parse tree produced by MiniDecafParser#primaryPostfix.
    def visitPrimaryPostfix(self, ctx: MiniDecafParser.PrimaryPostfixContext):
        return self.visit(ctx.primary())

    # Visit a parse tree produced by MiniDecafParser#callPostfix.
    def visitCallPostfix(self, ctx: MiniDecafParser.CallPostfixContext):
        name = ctx.IDENT().getText()
        if not name in self.declaredFuncTable:
            Err('call an undeclared function')
        funType = self.declaredFuncTable[name]
        if len(funType.paramTypes) != len(ctx.expr()):
            Err('number of para mismatch')
        for i in range(len(ctx.expr()) - 1, -1, -1):
            Type = self.RCast(self.visit(ctx.expr(i)))
            if not Type == funType.paramTypes[i]:
                Err('func param type mismatch')
            if i < 8:
                self.pop('a' + str(i))
        self.asm += '\tcall ' + name + '\n'
        self.push('a0')
        return funType.rtnType

    # Visit a parse tree produced by MiniDecafParser#numPrimary.
    def visitNumPrimary(self, ctx: MiniDecafParser.NumPrimaryContext):
        num = ctx.NUM()
        num_text = num.getText()
        if int(num_text) >= 2147483648:
            Err('too large number')
        self.asm += '\tli t0, ' + num_text + '\n'
        self.push('t0')
        return IntType()

    # Visit a parse tree produced by MiniDecafParser#identPrimary.
    def visitIdentPrimary(self, ctx: MiniDecafParser.IdentPrimaryContext):
        name = ctx.IDENT().getText()
        symbol = self.getSymbol(name)
        if symbol is not None:
            self.asm += '\taddi t0, fp, ' + str(symbol.offset) + '\n'
            self.push('t0')
            return symbol.ty
        elif name in self.declaredGlobalTable:
            # self.asm += '\tlui t1, %hi(' + name + ')\n'
            # # change sw to lw
            # self.asm += '\tlw t0, %lo(' + name + ')(t1)\n']
            self.asm += '\tla t0, ' + name + '\n'
            self.push('t0')
            return self.declaredGlobalTable[name]
        else:
            Err('undeclared symbol')

    # Visit a parse tree produced by MiniDecafParser#parenthesizedPrimary.
    def visitParenthesizedPrimary(self, ctx: MiniDecafParser.ParenthesizedPrimaryContext):
        return self.visit(ctx.expr())
