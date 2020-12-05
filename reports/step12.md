## Step 12 实验报告

2018011359 	计84 乐阳

### 实验过程

Step 12要求实现数组类型以及数组指针算术，具体而言分为如下步骤：

#### 1. 数组类型

在`type_zoo.py`中新添数组类型。相比其他类型，数组类型特有的两个字段是长度和基类型。

```python
class ArrayType:
    def __init__(self, baseType, length, value=True):
        self.ty = 'ARRAY'
        self.baseType = baseType
        self.size = length * baseType.getSize()
        self.rvalue = value
```

一个数组声明的文法为：

```
ty IDENT ('[' NUM ']')+ ';'
```

全局变量、局部变量的数据声明实现在`visitGlobalArrayDecl`和`visitLocalArrayDecl`中。二者流程类似，以后者为例：

```python
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
```

可见在构建数据类型的时候，先解析开头的基类型，再从右至左解析数组的各维度。比如`int a[2][3]`，类型解析的过程为：`int`类型 -> 基类型为`int`、长度为3的数组 -> 基类型为`int[3]`、长度为2的数组。

数组变量除了占据更大的一块空间，其他的性质与整数、指针没什么不同，我们不需要对全局、局部变量的存储和访问规则进行修改。

#### 2. 下标操作

下标操作是一种后缀一元运算符。

对于指针，`p[i]`相当于`*(p+i)`。只需要先对地址值做下标长度的偏移，再解引用即可。

对于数组，`a[i]`相对于`a`的地址的偏移为`i`倍的`a`的基类型（可能还是数组）的数据大小。

```python
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
```

#### 3. 指针运算

主要是对加减运算新添几条规则。需要注意指针之间不能做加法，指针之间可以相减，指针也可以减整数。

```python
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
```

### 思考题

1. 设有以下几个函数，其中局部变量 `a` 的起始地址都是 `0x1000`(4096)，请分别给出每个函数的返回值（用一个常量 minidecaf 表达式表示，例如函数 `A` 的返回值是 `*(int*)(4096 + 23 * 4)`）。

答：
- A：`*(int*)(4096 + 23 * 4)`
- B：`*(int*)(4096 + 23 * 4)`
- C：`*(int*)(4096 + (2 * 10 + 3) * 4)`
- D：`*(int*)((*(int**)(4096 + 2 * 4)) + 3 * 4)`
- E：`*(int*)((*(int**)(4096 + 2 * 4)) + 3 * 4)`




2. C 语言规范规定，允许局部变量是可变长度的数组，在我们的实验中为了简化，选择不支持它。请你简要回答，如果我们决定支持一维的可变长度的数组(即允许类似 `int n = 5; int a[n];` 这种，但仍然不允许类似 `int n = ...; int m = ...; int a[n][m];` 这种)，而且要求数组仍然保存在栈上（即不允许用堆上的动态内存申请，如`malloc`等来实现它），应该在现有的实现基础上做出那些改动？

答：编译原理课程第8讲曾介绍过，动态数组是通过内情向量的方式保存在栈帧中的。具体而言，栈内函数的活动记录中除了固定大小的局部数据区，还要包含动态数组区。在局部数据区中保存有动态数组的首地址和长度。

现有实现中是扫描完一个函数定义后，根据局部变量大小开辟定长的栈空间。加入动态数组后，需要添加开辟动态数组空间的语句，分配栈空间的大小是运行时确定的。此外在类型系统中需要添加动态数组类型（与静态数组不同）。

