## Step 1 实验报告

2018011359 	计84 乐阳

### 实验过程

本程序采用的方法是单次遍历语法分析树，直接生成汇编代码而不显式写出中间代码（参考实现为Java+Antlr4）。Antlr工具能自动执行词法分析和语法分析，生成一棵语法分析树。我们只需要利用其提供的`Visitor`模式逐一访问树的每个节点即可。程序的主体架构为：

```python
def main(argv):
    try:
        infile = argv[1]
        inputStream = FileStream(infile)	# 读入文件
        lexer = MiniDecafLexer(inputStream)	# 词法分析
        tokenStream = CommonTokenStream(lexer)	# 获得Token流

        parser = MiniDecafParser(tokenStream)	# 语法分析
        parser._errHandler = BailErrorStrategy() # 设置分析出错的应对方式
        tree = parser.prog()	# 生成语法分析树
        visitor = MainVisitor()
        visitor.visit(tree) # 访问语法分析树，生成汇编
        asm = visitor.asm
        print(asm)
        return 0
    except Exception as e:
        print(e, file=sys.stderr)
        return 1
```

Step1要求编译器能处理只有`main`函数且只有一个`return`常量语句的程序。语法规则为

```
grammar MiniDecaf;
prog:
	func EOF;

func: ty IDENT '(' ')' '{' stmt '}';

ty: 'int';

stmt: 'return' expr ';';

expr: NUM;
```

只需从程序中提取出返回值`NUM`，检查其符合`int`数据范围后存入`a0`寄存器即可。



### 思考题

1. 根据`minilexer`识别单词的正则表达式，可知其只能识别数字和字母。输入一个其他字符即可使其报错：

   ```python
   lexer.setInput("""\
       int main() {
           return -1;
       }
       """)
   ```

2. 构造词法符合`minilexer`但语法不正确的输入：

   ```python
   lexer.setInput("""\
       int main {
           return 233;
       }
       """)
   ```

3. `riscv`的32位返回值通常存储于`a0`，如果要返回64位数值则存储于`a0, a1`。