
class NoType:
    def __init__(self):
        self.type = "NO"
        # False means lvalue
        self.rvalue = True
        self.size = None

    def referenced(self):
        pass

    def dereferenced(self):
        pass

    def valueCast(self, value):
        self.rvalue = value

    def getSize(self):
        return self.size


class IntType:
    def __init__(self, value=True):
        self.type = "INT"
        # False means lvalue
        self.rvalue = value
        self.size = 4

    def referenced(self):
        pass

    def dereferenced(self):
        pass

    def valueCast(self, value):
        self.rvalue = value

    def getSize(self):
        return self.size


class FunType:
    def __init__(self, rtnType, paramTypes):
        self.type = "FUN"
        self.rtnType = rtnType
        self.paramTypes = paramTypes

    def equals(self, funType):
        if(self.rtnType.type != funType.rtnType.type):
            return False


class PointerType:
    def __init__(self, starNum):
        self.starNum = starNum
