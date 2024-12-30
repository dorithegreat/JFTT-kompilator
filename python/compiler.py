import ply.yacc as yacc
import ply.lex as lex

# Token declarations
tokens = (
    'LBR', 'FBR', 'LPAR', 'RPAR',
    'FOR', 'FROM', 'TO', 'DOWNTO', 'ENDFOR',
    'PROCEDURE', 'IS', 'BEGIN', 'END', 'PROGRAM',
    'IF', 'THEN', 'ELSE', 'ENDIF',
    'WHILE', 'DO', 'ENDWHILE', 
    'REPEAT', 'UNTIL',
    'READ', 'WRITE',
    'PID', 'NUM'
    'T',
    'ADD', 'SUB', 'MUL', 'DIV', 'MOD',
    'EQ', 'NEQ', 
    'GT', 'LT', 'GEQ', 'LEQ',
    'COM'
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

t_ADD = r'\+'
t_SUB = r'-'
t_MUL = r'\*'
t_DIV = r'\/'
t_MOD = r'\%'

t_ignore = r' \t'

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
