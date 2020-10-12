## Step 4 实验报告

2018011359 	计84 乐阳

### 实验过程

Step4要求实现比较和逻辑运算符，与数学运算的双目运算符的操作基本相同。利用RISC-V的条件置位指令可以实现比较运算。下面以比大小运算符为例

```python
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
```



### 思考题

1. 在表达式计算时，对于某一步运算，是否一定要先计算出所有的操作数的结果才能进行运算？

   答：否。C语言编译器对逻辑运算有短路求值特性，比如`0 && Expr`表达式的值直接为0，不会计算`Expr`的值。

2. 在 MiniDecaf 中，我们对于短路求值未做要求，但在包括 C 语言的大多数流行的语言中，短路求值都是被支持的。为何这一特性广受欢迎？你认为短路求值这一特性会给程序员带来怎样的好处？

   答：短路求值能提高表达式计算的效率，而且为程序员提供了很多方便。例如下面的例子，只有前一个表达式为真时后面一个表达式才被计算，因此程序不会发生错误。

   ```python
   if len(arr) > 2 and arr[2] == 1:
   	pass
   ```

   

