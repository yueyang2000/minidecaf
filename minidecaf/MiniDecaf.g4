grammar MiniDecaf;

prog:
    func EOF;

func: ty IDENT '(' ')' '{' stmt '}';

ty: 'int';

stmt: 'return' expr ';';

expr: lor;

lor: lor '||' lor | land;

land: land '&&' land | equ;

equ: equ ('==' | '!=') equ | rel;

rel: rel ('<'|'>'|'<='|'>=') rel | add;

add: add ('+' | '-') add | mul;

mul: mul ('*' | '/' | '%') mul | unary;

unary: ('-' | '!' | '~') unary | primary;

primary:
    NUM # numPrimary
    | '(' expr ')' # parenthesizedPrimary
    ;

/* lexer */
WS: [ \t\r\n\u000C] -> skip;

// comment
// The specification of minidecaf doesn't allow commenting,
// but we provide the comment feature here for the convenience of debugging.
COMMENT: '/*' .*? '*/' -> skip;
LINE_COMMENT: '//' ~[\r\n]* -> skip;

IDENT: [a-zA-Z_] [a-zA-Z_0-9]*;
NUM: [0-9]+;
