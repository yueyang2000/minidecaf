## Step 3 实验报告

2018011359 	计84 乐阳

### 实验过程

Step3要求实现多种双目数学运算符。双目运算符要注意优先级。`g4`文件中关于`Expression`解析的部分要由低优先级运算符递归调用高优先级运算符的解析，写法类似如下：

```
add: add ('+' | '-') add | mul;
mul: mul ('*' | '/' | '%') mul | unary;
unary: ('-' | '!' | '~') unary | primary;
```

此外双目操作与单目操作区别不大，只是前者要弹出栈顶两个元素做运算并将结果压栈。

```python
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
```

### 思考题

1. 请给出将寄存器 `t0` 中的数值压入栈中所需的 riscv 汇编指令序列；请给出将栈顶的数值弹出到寄存器 `t0` 中所需的 riscv 汇编指令序列。

   答：

   ```assembly
   addi sp, sp, -4		# t0压栈
   sw t0, 0(sp)
   
   lw t0, 0(sp)		# 出栈至t0
   addi sp, sp, 4
   ```

2. 语义规范中规定“除以零、模零都是未定义行为”，但是即使除法的右操作数不是 0，仍然可能存在未定义行为。请问这时除法的左操作数和右操作数分别是什么？

   答：左操作数为`0x80000000`，右操作数为`-1`时为未定义行为。

   ```C
   #include <stdio.h>
   
   int main() {
     int a = 0x80000000;	// 左操作数
     int b = -1;	// 右操作数
     printf("%d\n", a / b);
     return 0;
   }
   ```

   在MacOS 10.15.4（x86-64指令集）下运行会发生报错

   ```
   [1]    49551 floating point exception  ./test
   ```

   在RISC-V模拟器中编译运行得到结果

   ```
   -2147483648
   ```

   

