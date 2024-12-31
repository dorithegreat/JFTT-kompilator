import ply.yacc as yacc
import ply.lex as lex

# Token declarations
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
    'ASSIGN', 'SEMICOLON'
)

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

t_ASSIGN = r'\:\='
t_SEMICOLON = r'\;'

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

lex.lex()

# parser


# program_all - the main rule
# first declare the procedures, than the main function
def p_program_all(p):
    'program_all : procedures main'


# procedures - declaring procedures other than main
def p_procedures_decl(p):
    'procedures : procedures PROCEDURE proc_head IS declarations BEGIN commands END'

def p_procedures_no_decl(p):
    'procedures : procedures PROCEDURE proc_head IS BEGIN commands END'

def p_procedures_empty(p):
    'procedures : empty'


# main - rules for the main function
# no empty rule - valid program must have a main function
def p_main_decl(p):
    'main : PROGRAM IS declarations BEGIN commands END'

def p_main_no_decl(p):
    'main : PROGRAM IS BEGIN commands END'

# commands
def p_commands_commands(p):
    'commands : commands command'
    
def p_commands_end(p):
    'commands : command'

# command
def p_command_assign(p):
    'command : identifier ASSIGN identifier'

def p_command_if_else(p):
    'command : IF condition THEN commands ELSE commands ENDIF'

def p_command_if(p):
    'command : IF condition THEN commands ENDIF'

def p_command_while(p):
    'command : WHILE condition DO commands ENDWHILE'

def p_command_repeat_until(p):
    'command : REPEAT commands UNTIL condition SEMICOLON'

def p_command_for_to(p):
    'command : FOR PID FROM value TO value DO commands ENDFOR'

def p_command_for_downto(p):
    'command : FOR PID FROM value DOWNTO value DO commands ENDFOR'

def p_command_proc_call(p):
    'command : proc_call'

def p_command_read(p):
    'command : READ identifier SEMICOLON'

def p_command_write(p):
    'command : WRITE value SEMICOLON'


# proc_head
def p_proc_head(p):
    'proc_head : PID LPAR args_decl RPAR'

# proc_call
def p_proc_call(p):
    'proc_call : PID LPAR args RPAR'

# declarations
def p_declarations_decl_pid(p):
    '''declarations : declarations ',' PID'''

# declarations , pidentifier [ num : num ]
def p_declarations_decl_tab(p):
    '''declarations : declarations ',' PID LBR NUM ':' NUM RBR '''

def p_declarations_pid(p):
    'declarations : PID'

def p_declarations_tab(p):
    '''declarations :  PID LBR NUM ':' NUM RBR'''

# args_decl
def p_args_decl_ards_pid(p):
    'args_decl : args_decl PID'

def p_args_decl_ards_tab(p):
    'args_decl : args_decl T PID'

def p_args_decl_pid(p):
    'args_decl : PID'

def p_args_decl_tab(p):
    'args_decl : T PID'

# args
def p_args_args(p):
    'args : args PID'

def p_args_pid(p):
    'args : PID'

# expression - assignment to variables
def p_expr_value(p):
    'expression : value'

def p_expr_add(p):
    'expression : value ADD value'

def p_expr_sub(p):
    'expression : value SUB value'

def p_expr_mul(p):
    'expression : value MUL value'

def p_expr_div(p):
    'expression : value DIV value'

def p_expr_mod(p):
    'expression : value MOD value'

# condition
def p_cond_eq(p):
    'condition : value EQ value'

def p_cond_neq(p):
    'condition : value NEQ value'

def p_cond_gt(p):
    'condition : value GT value'

def p_cond_lt(p):
    'condition : value LT value'

def p_cond_geq(p):
    'condition : value GEQ value'

def p_cond_leq(p):
    'condition : value LEQ value'

# value
def p_value_num(p):
    'value : NUM'

def p_value_id(p):
    'value : identifier'

# identifier
def id_pid(p):
    'identifier : PID'

def id_tab_pid(p):
    'identifier : PID LBR PID RBR'

def id_tab_num(p):
    'identifier : PID LBR NUM RBR'

# empty rule for use in later empty productions
def p_empty(p):
    'empty :'
    pass

# yacc.yacc(start='program_all')