from symbol_table import SymbolTable
import nodes as nd

class CodeGenerator:
    def __init__(self, tree):
        self.tree : nd.Program = tree
        self.symbols = SymbolTable()
        self.procedures = dict()
        
        # list of strings 
        self.code = []
        
    
    def generate(self):
        # all functions keep track of how many lines they added, for the purpose on calculating jumps
        
        # starting from 0 because the vm numbers lines from 0, despite all editors numbering from 1
        # just to be annoying
        linenum_after_procedures = self.generate_procedures(self.tree.procedures, 0)
        self.generate_main(self.tree.main, linenum_after_procedures)
    
    
    def generate_procedures(self, procedures : nd.Procedures, linenum):
        for proc in procedures.procedures:
            linenum = self.generate_procedure(linenum)
    
    #? distinct from generate_procedures()
    # that one is plural, this one is singular
    def generate_procedure(self, procedure : nd.Procedure, linenum):
        procedure_name = procedure.proc_head.pid
        
        # add to the procedure table the line number of this procedure
        self.procedures.setdefault(procedure_name, linenum)
        
        # TODO do something with arguments
        # arguments will be in the  first few memory cells starting with 1, before variables
        # will appear in order of declaration
        
        # allocating memory for variables
        for var in procedure.declaration.declarations:
            self.symbols.add_variable(var)
            
        self.generate_commands(procedure.commands)
        
    
    def generate_main(self, main : nd.Main, linenum):
        # TODO if I leave it like this no variable name can repeat between main and the procedures
        # I should probably reset symbol table after every procedure
        # actually I should't, the procedures will also get called later
        # in that case I should probably prepend the procedure name to the variable name in the symbol table
        for var in main.declarations:
            self.symbols.add_variable(var)
        pass
    
    def generate_commands(self, commands : nd.Commands, linenum):
        for comm in commands.commands:
            if type(comm) == nd.Assign:
                self.code.append("LOAD ", self.symbols.get_variable(comm.variable))
                linenum += 1;
                linenum = self.generate_expression(comm.assignment, linenum)
                
                
            elif type(comm) == nd.IfStatement:
                linenum = self.generate_ifstatement(comm, linenum)
            elif type(comm) == nd.WhileLoop:
                linenum = self.generate_while(comm, linenum)
            elif type(comm) == nd.RepeatUntil:
                linenum = self.generate_repeat_until(comm, linenum)
            elif type(comm) == nd.ForTo:
                pass
            elif type(comm) == nd.ForDownto:
                pass
            elif type(comm) == nd.ProcCall:
                pass
            # TODO  elif type(comm) == READ
        
        return linenum
                
    
    def generate_ifstatement(self, ifstatement : nd.IfStatement):
        # TODO optimize for unreachable code blocks
        # like if 1 > 2 
        
        # TODO evaluate condition
        self.generate_commands(ifstatement.commands)
        
        if ifstatement.else_commands is not None:
            self.generate_commands(ifstatement.else_commands)
            
    def generate_while(self, whileloop : nd.WhileLoop):
        # TODO evaluate condition
        self.generate_commands(whileloop.commands)
        
    def generate_repeat_until(self, repeat : nd.RepeatUntil):
        pass
    
    def generate_expression(self, expression : nd.Expression, linenum):
        
        # TODO if both are numbers just calculate it
        
        # TODO include code for constants
        if expression.operator == "ADD":\
            # perform addition
            self.code.append("LOAD ", self.symbols.get_variable(expression.value1))
            self.code.append("ADD ", self.symbols.get_variable(expression.value2))
            # returns result to 1
            # I assume the function that called this will do something with it
            # this will likely need to get optimized for not having consecutive stores and loads on the same register
            self.code.append("STORE 1")
            
            #! important to change if I ever change the code above
            # for that reason I should change it so it's not this easy to mess up
            # but also. it works
            return linenum + 3
        
        if expression.operator == "SUB":
            self.code.append("LOAD ", self.symbols.get_variable(expression.value1))
            self.code.append("SUB ", self.symbols.get_variable(expression.value2))
            self.code.append("STORE 1")
            
            return linenum + 3
            
            # perform subtraction
            pass
        
        if expression.operator == "MUL":
            # self.multiplication()
            pass
        
        if expression.operator == "DIV":
            # self.division()
            pass
        
        if expression.operator == "MOD":
            # self.modulo()
            
            pass
        