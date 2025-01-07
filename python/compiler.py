import ply.yacc as yacc
import ply.lex as lex

import nodes as nd
from code_generator import CodeGenerator

#* Token declarations

# massive amount of tokens because I don't like literals
tokens = (
    'LBR', 'RBR', 'LPAR', 'RPAR',
    'FOR', 'FROM', 'TO', 'DOWNTO', 'ENDFOR',
    'PROCEDURE', 'IS', 'BEGIN', 'END', 'PROGRAM',
    'IF', 'THEN', 'ELSE', 'ENDIF',
    'WHILE', 'DO', 'ENDWHILE', 
    'REPEAT', 'UNTIL',
    'READ', 'WRITE',
    'PID', 'NUM',
    'T',
    'ADD', 'SUB', 'MUL', 'DIV', 'MOD',
    'EQ', 'NEQ', 
    'GT', 'LT', 'GEQ', 'LEQ',
    'COM',
    'ASSIGN', 'SEMICOLON', 'COMMA'
)

#* token definitions

t_FOR = r'FOR'
t_FROM = r'FROM'
t_TO = r'TO'
t_DOWNTO = r'DOWNTO'
t_ENDFOR = r'ENDFOR'

t_PROCEDURE = r'PROCEDURE'
t_IS = r'IS'
t_BEGIN = r'BEGIN'
t_END = r'END'
t_PROGRAM = r'PROGRAM'

t_IF = r'IF'
t_THEN = r'THEN'
t_ELSE = r'ELSE'
t_ENDIF = r'ENDIF'

t_WHILE = r'WHILE'
t_DO = r'DO'
t_ENDWHILE = r'ENDWHILE'

t_REPEAT = r'REPEAT'
t_UNTIL = r'UNTIL'

t_READ = r'READ'
t_WRITE = r'WRITE'

t_T = r'T'

t_LBR = r'\['
t_RBR = r'\]'
t_LPAR = r'\('
t_RPAR = r'\)'

t_COM = r'\#.*'
t_PID = r'[_a-z]+'

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'\/'
t_MOD = r'\%'

t_EQ = r'\='
t_NEQ = r'\!='
t_GEQ = r'>='
t_LEQ = r'<='
t_LT = r'<'
t_GT = r'>'

t_ASSIGN = r'\:\='
t_SEMICOLON = r'\;'
t_COMMA = r','

t_ignore = ' \t'

# number string to int
def t_NUM(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

    
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


def t_error(t):
    print(f'\ninvalid character: {t.value[0]!r}')
    t.lexer.skip(1)

# lex.lex()

# * parser

tree = None

# program_all - the main rule
# first declare the procedures, than the main function
def p_program_all(p):
    'program_all : procedures main'
    p[0] = nd.Program(p[1], p[2])


# procedures - declaring procedures other than main
def p_procedures_decl(p):
    'procedures : procedures PROCEDURE proc_head IS declarations BEGIN commands END'
    p[1].add_procedure(nd.Procedure(p[3], p[5], p[7]))

def p_procedures_no_decl(p):
    'procedures : procedures PROCEDURE proc_head IS BEGIN commands END'
    p[1].add_procedure(nd.Procedure(p[3], None, p[6]))
    p[0] = p[1]

def p_procedures_empty(p):
    'procedures : empty'
    # creates an empty list of procedures
    p[0] = nd.Procedures()


# main - rules for the main function
# no empty rule - valid program must have a main function
def p_main_decl(p):
    'main : PROGRAM IS declarations BEGIN commands END'
    p[0] = nd.Main(p[3], p[5])

def p_main_no_decl(p):
    'main : PROGRAM IS BEGIN commands END'
    p[0] = nd.Main(None, p[4])

# commands
def p_commands_commands(p):
    'commands : commands command'
    p[1].add_command(p[2])
    p[0] = p[1]
    
def p_commands_end(p):
    'commands : command'
    commands = nd.Commands()
    commands.add_command(p[1])
    p[0] = commands

# command
def p_command_assign(p):
    'command : identifier ASSIGN expression SEMICOLON'
    p[0] = nd.Assign(p[1], p[3])
    

def p_command_if_else(p):
    'command : IF condition THEN commands ELSE commands ENDIF'
    p[0] = nd.IfStatement(p[2], p[4], p[6])

def p_command_if(p):
    'command : IF condition THEN commands ENDIF'
    p[0] = nd.IfStatement(p[2], p[4], None)

def p_command_while(p):
    'command : WHILE condition DO commands ENDWHILE'
    p[0] = nd.WhileLoop(p[2], p[4])

def p_command_repeat_until(p):
    'command : REPEAT commands UNTIL condition SEMICOLON'
    p[0] = nd.RepeatUntil(p[2], p[4])

def p_command_for_to(p):
    'command : FOR PID FROM value TO value DO commands ENDFOR'
    p[0] = nd.ForTo(p[2], p[4], p[6], p[8])

def p_command_for_downto(p):
    'command : FOR PID FROM value DOWNTO value DO commands ENDFOR'
    p[0] = nd.ForTo(p[2], p[4], p[6], p[8])

def p_command_proc_call(p):
    'command : proc_call'
    p[0] = p[1]

def p_command_read(p):
    'command : READ identifier SEMICOLON'
    p[0] = nd.Read(p[2])

def p_command_write(p):
    'command : WRITE value SEMICOLON'
    p[0] = nd.Write(p[2])


# proc_head
def p_proc_head(p):
    'proc_head : PID LPAR args_decl RPAR'
    p[0] = nd.ProcHead(p[1], p[3])

# proc_call
def p_proc_call(p):
    'proc_call : PID LPAR args RPAR'
    p[0] = nd.ProcCall(p[1], p[3])

# declarations
def p_declarations_decl_pid(p):
    '''declarations : declarations COMMA PID'''
    p[1].add_declaration(p[3])
    p[0] = p[1]

# declarations , pidentifier [ num : num ]
def p_declarations_decl_tab(p):
    '''declarations : declarations COMMA PID LBR NUM ':' NUM RBR '''
    p[1].add_declaration(nd.Array(p[3], p[5], p[7]))
    p[0] = p[1]

def p_declarations_pid(p):
    'declarations : PID'
    declarations = nd.Declarations()
    declarations.add_declaration(p[1])
    p[0] = declarations

def p_declarations_tab(p):
    '''declarations :  PID LBR NUM ':' NUM RBR'''
    declarations = nd.Declarations()
    declarations.add_declaration(nd.Array(p[1], p[3], p[5]))
    p[0] = declarations

# args_decl
#* for now argument declarations use the same Array class as array declarations


def p_args_decl_ards_pid(p):
    'args_decl : args_decl PID'
    p[1].add_arg(p[2])
    p[0] = p[1]

def p_args_decl_ards_tab(p):
    'args_decl : args_decl T PID'
    p[1].add_arg(nd.Array(p[3], None, None))
    p[0] = p[1]

def p_args_decl_pid(p):
    'args_decl : PID'
    ad = nd.ArgsDecl()
    ad.add_arg(p[1])
    p[0] = p[1]

def p_args_decl_tab(p):
    'args_decl : T PID'
    ad = nd.ArgsDecl()
    ad.add_arg(nd.Array(p[2], None, None))
    p[0] = p[1]

# args
def p_args_args(p):
    'args : args PID'
    p[1].add_arg(p[2])
    p[0] = p[1]

def p_args_pid(p):
    'args : PID'
    arg = nd.Args()
    arg.add_arg(p[1])
    p[0] = p[1]

# expression - assignment to variables
def p_expr_value(p):
    'expression : value'
    p[0] = nd.Expression(p[1], None, None)

def p_expr_add(p):
    'expression : value ADD value'
    p[0] = nd.Expression(p[1], "ADD", p[3])

def p_expr_sub(p):
    'expression : value SUB value'
    p[0] = nd.Expression(p[1], "SUB", p[3])

def p_expr_mul(p):
    'expression : value MUL value'
    p[0] = nd.Expression(p[1], "MUL", p[3])

def p_expr_div(p):
    'expression : value DIV value'
    p[0] = nd.Expression(p[1], "DIV", p[3])

def p_expr_mod(p):
    'expression : value MOD value'
    p[0] = nd.Expression(p[1], "MOD", p[3])

# condition
def p_cond_eq(p):
    'condition : value EQ value'
    p[0] = nd.Condition(p[1], "EQ", p[3])

def p_cond_neq(p):
    'condition : value NEQ value'
    p[0] = nd.Condition(p[1], "NEQ", p[3])

def p_cond_gt(p):
    'condition : value GT value'
    p[0] = nd.Condition(p[1], "GT", p[3])

def p_cond_lt(p):
    'condition : value LT value'
    p[0] = nd.Condition(p[1], "LT", p[3])

def p_cond_geq(p):
    'condition : value GEQ value'
    p[0] = nd.Condition(p[1], "GEQ", p[3])

def p_cond_leq(p):
    'condition : value LEQ value'
    p[0] = nd.Condition(p[1], "LEQ", p[3])

# value
def p_value_num(p):
    'value : NUM'
    p[0] = p[1]

def p_value_id(p):
    'value : identifier'
    p[0] = p[1]

# identifier
def p_id_pid(p):
    'identifier : PID'
    p[0] = nd.Identifier(p[1])

def p_id_tab_pid(p):
    'identifier : PID LBR PID RBR'
    p[0] = nd.ArrayPosition(p[1], p[3])

def p_id_tab_num(p):
    'identifier : PID LBR NUM RBR'
    p[0] = nd.ArrayPosition(p[1], p[3])

# empty rule for use in later empty productions
def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p != None:
        print('\nsyntax error: ', p.value)
    else:
        print(f'syntax error')

# yacc.yacc(start='program_all')


import logging
logging.basicConfig(
    level = logging.DEBUG,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

lex.lex(debug=True,debuglog=log)
parser = yacc.yacc(debug=True,debuglog=log)

text = '''
PROGRAM IS
	n, p
BEGIN
    READ n;
    REPEAT
	p:=n/2;
	p:=2*p;
	IF n>p THEN 
	    WRITE 1;
	ELSE 
	    WRITE 0;
	ENDIF
	n:=n/2;
    UNTIL n=0;
END
'''
tree = parser.parse(text, debug=log)

codegen = CodeGenerator(tree)
codegen.generate()

for line in codegen.code:
    print(line)