## Step 8 实验报告

2018011359 	计84 乐阳

### 实验过程

step 8 要实现循环语句，具体而言要实现`for`循环、`do while`循环、`while`循环、`break`和`continue`语句，循环可以嵌套。

以`for`循环为例，语句结构为

```c
for( init_stmt; cond_stmt; update_stmt){
	loop;
}
```

翻译为汇编大致如下。如遇到`continue`则跳转至`.continueLoop`，遇到`break`则跳转至`afterLoop`。

```assembly
	# init_stat
.beforeLoop
	# calculate cond_stmt
	lw t1, 0(sp)
	addi sp, sp, 4
	beqz t1, .afterLoop
.continueLoop
	# loop body
	j .beforeLoop
.afterLoop
```

注意`for`语句单独有一个作用域，循环体是另一个作用域。循环可以嵌套，实现时为循环加上标号，如`beforeLoop0, afterLoop0`等。其他的循环语句也类似。



### 思考题

从执行的指令的条数这个角度（`label` 指令不计算在内，假设循环体至少执行了一次），请评价这两种翻译方式哪一种更好？

答：第二种方法更好。第一种方法有一个无条件跳转`br BEGINLOOP_LABEL`，在跳出循环时一共要进行两次跳转；而第二种方法只需要一次跳转即可结束循环。

