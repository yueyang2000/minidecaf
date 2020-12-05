## Step 11 实验报告

2018011359 	计84 乐阳

### 实验过程

Step11 要求实现指针类型，具体而言就是引入类型系统和相关的检查。

#### 1. 类型系统

本编译器的类型系统定义在`type_zoo.py`中，其实前几个阶段已经用过其中的`NoType`、`IntType`、和`FunType`。主要用来比对函数调用时参数的类型和个数是否完全匹配。为了使类型系统趋于完整，为每个类型添加引用、解引用接口`reference(), dereference()`，左右值转换接口`valueCast`。为了实现方便，一个类型对象刚刚创建时，默认`rvalue=true`，即右值。

新建指针类型`PointerType`，指针比其他的类型多了一个引用次数的字段`starNum`，类型比较时引用次数也要匹配。

```python
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
```

#### 2. 类型检查

类型系统参考了Java-ANTLR的实现，为语法树中每个节点绑定一个类型。根据类型系统的规则，节点的类型其实就是一个属性文法的规约过程。如果这个节点是一个运算式，那它的类型就是运算结果的类型；如果不是一个用于“求值”的节点，那么它的类型为`NoneType`。

在生成的汇编中，寄存器中保存左值地址、右值的数值。因此每次要对左值变量表达式做运算时要进行左右值转换，实现在`RCast`函数中：

```python
def RCast(self, Type):
    if Type.rvalue == False:
        self.pop('t0')
        self.asm += '\tlw t0, 0(t0)\n'
        self.push('t0')
	return Type.valueCast(True)
```

例如对于`==`运算符比较两个变量，流程大致如下。可见对两个操作数做右值转换、比较两个操作数类型是否相同等步骤。

```python
leftType = self.RCast(self.visit(ctx.equ(0)))
rightType = self.RCast(self.visit(ctx.equ(1)))
if not leftType == rightType:
    Err('type mismatch')
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
```

#### 3. 指针的一元运算

一元运算符主要是增减引用，反映到指针上其实就是`starNum`个数的增减。

```python
        if op == '*':
            return self.RCast(Type).dereferenced()
        elif op == '&':
            return Type.referenced()
```

### 思考题

1. 为什么类型检查要放到名称解析之后？

答：名称解析将名称关联到对应的变量，进而知道名称所对应的类型信息。只有知道了表达式中每个符号的类型，才能应用类型运算规则判断是否合法。



2. MiniDecaf 中一个值只能有一种类型，但在很多语言中并非如此，请举出一个反例。

答：C语言支持`union`共用体，可以视同一块内存里的数据值为多种不同的类型。



3. 在本次实验中我们禁止进行指针的比大小运算。请问如果要实现指针大小比较需要注意什么问题？可以和原来整数比较的方法一样吗？

答：需要注意必须是类型相同的指针才能比较大小。将指针视作等宽的无符号整数进行比较即可。

