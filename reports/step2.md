## Step 2 实验报告

2018011359 	计84 乐阳

### 实验过程

程序是单遍扫描，没有显式的IR生成，但还是需要实现栈机的逻辑——操作数的压栈和出栈。具体的代码为

```python
    def push(self, reg):
        # 将reg存放的数压栈
        self.asm += '# push ' + reg + "\n"
        self.asm += '\taddi sp, sp, -4\n'
        self.asm += '\tsw ' + reg + ', 0(sp)\n'

    def pop(self, reg):
        # 弹出栈顶，保存在reg
        self.asm += '# pop ' + reg + '\n'
        self.asm += '\tlw ' + reg + ', 0(sp)\n'
        self.asm += '\t addi sp, sp, 4\n'
```

Step 2要求实现三种单目运算符。语法可以表示为

```
unary: ('-' | '!' | '~') unary | primary;
```

当访问到`primary`节点时，读出操作数并压栈。执行单目运算就是对栈顶元素执行相应的运算。

```python
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
```



### 思考题

1. 请设计一个表达式，只使用`-~!`这三个单目运算符和 $[0, 2^{31} - 1]$ 范围内的非负整数，使得运算过程中发生越界。

   答：表达式`-~(2147483647)`会在`-`运算时发生溢出。