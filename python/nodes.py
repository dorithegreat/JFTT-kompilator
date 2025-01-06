from __future__ import annotations

# classes representing syntax structures for the purpose of building an abstract syntax tree
# yacc internally generates but doesn't store or expose an AST
# hence the need for implicitly building one if it's necessary to refer to parts of the structure outside of the initial parsing

class Args:
    def __init__(self):
        self.arguments = []

    def add_arg(self, arg):
        self.arguments.append(arg)

class ArgsDecl:
    def __init__(self):
        self.arguments = []

    def add_arg(self, arg):
        self.arguments.append(arg)

class Array:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

class ArrayPosition:
    def __init__(self, name, position):
        self.name = name
        self.position = position

class Assign:
    def __init__(self, variable, assignment):
        self.variable = variable
        self.assignment : Expression = assignment

class Commands:
    def __init__(self):
        self.commands = []

    def add_command(self, command):
        self.commands.append(command)

class Condition:
    def __init__(self, value1, operator, value2):
        self.value1 = value1
        self.value2 = value2
        self.operator = operator

class Declarations:
    def __init__(self):
        self.declarations = []

    def add_declaration(self, declaration):
        self.declarations.append(declaration)

class Expression:
    def __init__(self, value1, operator, value2):
        self.value1 = value1
        # value2 and operator may be None in the case expression -> value
        self.value2 = value2
        self.operator = operator

class ForDownto:
    def __init__(self, iterator, start_value, end_value, commands):
        self.iterator = iterator
        self.start_value = start_value
        self.end_value = end_value
        self.commands = commands

class ForTo:
    def __init__(self, iterator, start_value, end_value, commands):
        self.iterator = iterator
        self.start_value = start_value
        self.end_value = end_value
        self.commands = commands

class Identifier:
    def __init__(self, name):
        self.name = name

class IfStatement:
    def __init__(self, condition, commands, else_commands):
        self.condition = condition
        self.commands = commands
        # else commands are None if there is no else
        self.else_commands = else_commands

class Main:
    def __init__(self, declarations, commands):
        # declarations may be None if the program does not define any variables at all~
        self.declarations : Declarations = declarations
        self.commands : Commands = commands

class ProcCall:
    def __init__(self, pid, arguments):
        self.args = arguments
        self.pid = pid

class ProcHead:
    def __init__(self, pid, args_decl):
        self.pid = pid
        self.args_decl = args_decl

class Procedure:
    def __init__(self, proc_head, declaration, commands):
        self.proc_head : ProcHead = proc_head
        self.declaration : Declarations = declaration
        self.commands : Commands = commands

class Procedures:
    def __init__(self):
        self.procedures: list[Procedure] = []

    def add_procedure(self, procedure: Procedure):
        self.procedures.append(procedure)

    # I don't think this class needs to support removing a procedure

class Program:
    def __init__(self, procedures, main):
        self.procedures = procedures
        self.main = main

class RepeatUntil:
    def __init__(self, commands, condition):
        self.condition = condition
        self.commands = commands

class WhileLoop:
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands
