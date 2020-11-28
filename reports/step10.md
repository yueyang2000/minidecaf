## Step 10 实验报告

2018011359 	计84 乐阳

### 实验过程

本阶段要求实现全局变量。类似于函数，我们引入专门的符号表`declaredGlobalTable`和`initializedGlobalTable`来处理全局变量。

全局变量的访问实现于函数`visitGlobalDecl`。就地初始化的全局变量存储在`.data`段中，例如全局变量定义`int A = 1;`翻译为

```assembly
.data
.global A
A:
	.quad	1
```

在整个程序扫描结束后，将所有未初始化全局变量送入BSS段，使用`.comm`语法。

读取全局变量实现在`visitIdentPrimary`函数中，利用伪指令`la`很容易实现。

### 思考题

1. 请给出将全局变量 `a` 的值读到寄存器 `t0` 所需的 riscv 指令序列。

答：

```assembly
la	t0, a
lw	t0, (t0)
```

