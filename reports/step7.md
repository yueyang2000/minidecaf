## Step 7 实验报告

2018011359 	计84 乐阳

### 实验过程

step7 要求实现程序的作用域，在C语言中用`{}`表示。每一个函数、`if, while`等语句块等都有自己的作用域。作用域层层嵌套，符号查找从内向外进行。

在前面6个步骤中，我们用一个字典`symbolTable`来作为局部变量的符号表，相当于只有一层作用域。在引入作用域嵌套后，需要将`symbolTable`实现为一个栈，每进入一个语句块就将一个新作用域入栈，每出一个语句块就将栈顶作用域弹出，每声明一个局部变量就保存在当前栈顶的作用域中（表示当前的作用域）。遇到一个局部变量符号则按顺序从内层作用域向外层查找。

访问一个块语句的语法树的代码为：

```python
def visitBlockStmt(self, ctx: MiniDecafParser.BlockStmtContext):
    self.symbolTable.append({}) # 入栈一个新作用域
    for block in ctx.blockItem():
        self.visit(block)
    self.symbolTable.pop()	# 访问块语句完毕，出栈
```



### 思考题

1. 答：需要填下的空为`x=0`，程序执行最后一条`return x`指令，这个`x`是外层作用域声明的`x`，其值为0。

```C
int main() {
 	int x = 0;
 	if (x) {
        return x;
    } 
    else{
     	int x = 2;
 	}
 	return x;
}
```



2. 在实验指导中，我们提到“就 MiniDecaf 而言，名称解析的代码也可以嵌入 IR 生成里”，但不是对于所有语言都可以把名称解析嵌入代码生成。试问被编译的语言有什么特征时，名称解析作为单独的一个阶段在 IR 生成之前执行会更好？

   答：有变量提升特征的语言，最好把名称解析作为一个单独的阶段。例如javascript语言中，程序会首先扫描该作用域中的所有声明，再顺序执行作用域中的语句，也就是说可以先使用再声明变量。
