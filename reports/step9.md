## Step 9 实验报告

2018011359 	计84 乐阳

### 实验过程

本阶段要实现函数调用。函数是一种与之前不同的符号类型，代码中`funType`定义了函数类型：

```python
class FunType:
    def __init__(self, rtnType, paramTypes):
        self.ty = "FUN"
        self.rtnType = rtnType
        self.paramTypes = paramTypes
```

函数类型包括返回值类型以及参数列表中每个参数的类型。在比较两个函数类型是否相等时，返回值类型和参数的数目、类型都要匹配。

为函数设置专门的符号表`declaredFuncTable`和`definedFuncTable`。声明、调用函数时要在其中查找是否匹配、是否存在冲突。C语言中函数不存在块作用域问题，可以看做全局符号。

访问一个函数的流程实现在`visitDefinedFunc`函数中。具体而言，它和前面几个step中访问主函数没有太多不同。唯一添加的传递参数的语句：

```python
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
                paramName, -4 * i, funType.paramTypes[i - 1])
            else:
                field[paramName] = Symbol(
                    paramName, 4 * (i - 9 + 2), funType.paramTypes[i - 1])
self.symbolTable.append(field)
```

函数的参数算作一个单独的作用域。在分析函数调用语句时一边将建立参数作用域`Field`，同时按照汇编传参标准进行传参：前8个参数用寄存器`a0~a7`传递，其余参数从右至左存于栈中。

### 思考题

1. MiniDecaf 的函数调用时参数求值的顺序是未定义行为。试写出一段 MiniDecaf 代码，使得不同的参数求值顺序会导致不同的返回结果。

答：考虑如下的例子：

```C
int glob = 0;
int func1(){
    glob = 1;
    return glob;
}
int func2(){
    return glob + 1;
}
int add(int a, int b){
    return a + b;
}
int main(){
    int res = add(func1(), func2());
}
```

如果从左至右进行参数求值，`res = add(1, 2) = 3`

如果从右至左进行参数求值，`res = add(1, 1) = 2`

可见不同参数求值顺序导致不同结果。

