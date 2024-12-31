# classes representing syntax structures for the purpose of building an abstract syntax tree
# yacc internally generates but doesn't store or expose an AST
# hence the need for implicitly building one if it's necessary to refer to parts of the structure outside of the initial parsing

class Identifier:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class IfStatement:
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

class Condition:
    def __init__(self, value1, operator, value2):
        self.value1 = value1
        self.value2 = value2
        self.operator = operator\
        

class Expression:
    def __init__(self, value1, operator, value2):
        self.value1 = value1
        # value2 and operator may be None in the case expression -> value
        self.value2 = value2
        self.operator = operator

class Program:
    def __init__(self, procesures, main):
        self.procedures = procesures
        self.main = main

class Main:
    def __init__(self, declarations, commands):
        # declarations may be None if the program does not define any variables at all
        self.declarations = declarations
        self.commands = commands