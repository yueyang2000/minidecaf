class Symbol:
    def __init__(self, name, offset, ty):
        self.name = name
        self.offset = int(offset)
        self.ty = ty


class NoType:
    def __init__(self):
        self.ty = "NO"
        # False means lvalue
        self.rvalue = True
        self.size = None

    def __eq__(self, obj):
        return self.ty == obj.ty and self.rvalue == obj.rvalue

    def referenced(self):
        raise Exception('referenced unsupport')

    def dereferenced(self):
        raise Exception('dereference unsupport')

    def valueCast(self, value):
        raise Exception('value Cast not support')

    def getSize(self):
        raise Exception('getSize not support')


class IntType:
    def __init__(self, value=True):
        self.ty = "INT"
        # False means lvalue
        self.rvalue = value
        self.size = 4

    def __eq__(self, obj):
        return self.ty == obj.ty and self.rvalue == obj.rvalue

    def referenced(self):
        if self.rvalue == False:
            return PointerType(1)
        else:
            raise Exception('reference rvalue int')

    def dereferenced(self):
        raise Exception('dereference unsupport')

    def valueCast(self, value):
        return IntType(value)

    def getSize(self):
        return self.size


class FunType:
    def __init__(self, rtnType, paramTypes):
        self.ty = "FUN"
        self.rtnType = rtnType
        self.paramTypes = paramTypes

    def __eq__(self, funType):
        if self.rtnType.ty != funType.rtnType.ty:
            return False
        if len(self.paramTypes) != len(funType.paramTypes):
            return False
        for paramType in self.paramTypes:
            contains = False
            for t1 in funType.paramTypes:
                if paramType.ty == t1.ty:
                    contains = True
            if not contains:
                return False
        return True


class PointerType:
    def __init__(self, starNum, value=True):
        self.ty = "POINTER"
        self.starNum = starNum
        self.rvalue = value
        self.size = 4

    def __eq__(self, Type):
        return Type.ty == "POINTER" and self.starNum == Type.starNum and self.rvalue == Type.rvalue

    def referenced(self):
        if self.rvalue == False:
            return PointerType(self.starNum + 1)
        else:
            raise Exception('reference rvalue pointer')

    def dereferenced(self):
        if self.starNum > 1:
            return PointerType(self.starNum - 1, False)
        else:
            return IntType(False)

    def valueCast(self, value):
        return PointerType(self.starNum, value)

    def getSize(self):
        return self.size


class ArrayType:
    def __init__(self, baseType, length, value=True):
        self.ty = 'ARRAY'
        self.baseType = baseType
        self.size = length * baseType.getSize()
        self.rvalue = value

    def __eq__(self, Type):
        return Type.ty == self.ty and Type.size == self.size and self.baseType == Type.baseType

    def referenced(self):
        raise Exception('reference unsupport')

    def dereferenced(self):
        raise Exception('dereference unsupport')

    def valueCast(self, value):
        if value == False:
            raise Exception('array must be lvalue')
        else:
            return self

    def getSize(self):
        return self.size
