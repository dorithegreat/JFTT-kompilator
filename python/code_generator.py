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
            
        return linenum
    
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
            
        linenum = self.generate_commands(procedure.commands, linenum)
        
        return linenum
        
    
    def generate_main(self, main : nd.Main, linenum):
        # TODO if I leave it like this no variable name can repeat between main and the procedures
        # I should probably reset symbol table after every procedure
        # actually I should't, the procedures will also get called later
        # in that case I should probably prepend the procedure name to the variable name in the symbol table
        for var in main.declarations.declarations:
            self.symbols.add_variable(var)
        pass
    
        linenum = self.generate_commands(main.commands, linenum)
    
    # TODO change linenum to be the number of lines added
    # not whatever this mess currently is
    def generate_commands(self, commands : nd.Commands, linenum):
        inner_code = []
        
        for comm in commands.commands:
            if type(comm) == nd.Assign:
                inner_code.append("LOAD ", self.symbols.get_variable(comm.variable))
                linenum += 1;
                linenum = self.generate_expression(comm.assignment, linenum)
                
                
            elif type(comm) == nd.IfStatement:
                linenum, c = self.generate_ifstatement(comm, linenum)
                inner_code += c
            elif type(comm) == nd.WhileLoop:
                linenum, c = self.generate_while(comm, linenum)
                inner_code += c
            elif type(comm) == nd.RepeatUntil:
                linenum, c = self.generate_repeat_until(comm, linenum)
                inner_code += c
            elif type(comm) == nd.ForTo:
                pass
            elif type(comm) == nd.ForDownto:
                pass
            elif type(comm) == nd.ProcCall:
                pass
            elif type(comm) == nd.Read:
                inner_code.append(f"GET {self.symbols.get_variable(comm.variable.name)}")
                linenum += 1
                
            elif type(comm) == nd.Write:
                inner_code.append("PUT " + self.symbols.get_variable(comm.value))
                linenum += 1
        
        return linenum, inner_code
                
    
    def generate_ifstatement(self, ifstatement : nd.IfStatement, linenum):
        inner_code = []
        
        # TODO optimize for unreachable code blocks
        # like if 1 > 2 
        
        # TODO evaluate condition
        
        #! THIS IS ALL TRASH
        # if block should come first because if else doesn't exist there's nothing to jump to
        # wait no
        # in any case, there should be a jump to skip if, if the condition is false
        # though if there is an else block there would need to be a second jump to bypass if
        # if there's no else block the only jump is to bypass if or not
        # so if block should come first, so there's only a jump to skip if, and a jump to skip else after if was executed
        # I think? it might not have much significance at all
        # it's also possible to do either one first based on which code is shorter
        #? damn what a mess
        
        # line_if, code_if = self.generate_commands(ifstatement.commands, linenum)
        
        # line_else = None
        # if ifstatement.else_commands is not None:
        #     line_else, code_else = self.generate_commands(ifstatement.else_commands, linenum)
        # else:
        #     # if there's no else, linenum after else is the same as linenum
        #     line_else = linenum
        
        # # if true jump to line number before if, which is line_if
        # # if false jump to line number before else, which is linenum
        # # else comes first, then if
        # line_cond, code_cond = self.generate_condition(ifstatement.condition, linenum, line_else, linenum)
            
    def generate_while(self, whileloop : nd.WhileLoop):
        # TODO evaluate condition
        self.generate_commands(whileloop.commands)
        
    def generate_repeat_until(self, repeat : nd.RepeatUntil, lineneum):
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
        
    def generate_condition(self, condition : nd.Condition, linenum, jump_if_true, jump_if_false):
        # TODO optimize for already known conditions like 1 = 2
        
        # TODO make it work with arrays, variables and constants
        
        if condition.operator == "EQ":
            self.code.append(f"LOAD {self.symbols.get_variable(condition.value1)}")
            self.code.append(f"SUB {self.symbols.get_variable(condition.value2)}")
            self.code.append(f"JZERO {jump_if_true}")
            # should I include jumping if false?
            
            return linenum + 3
        
        elif condition.operator == "NEQ":
            self.code.append(f"LOAD {self.symbols.get_variable(condition.value1)}")
            self.code.append(f"SUB {self.symbols.get_variable(condition.value2)}")
            
            # if it's either positive and negative then the condition is true
            # TODO do it smarter
            self.code.append(f"JPOS {jump_if_true}")
            self.code.append(f"JNEG {jump_if_true}")
            
            return linenum + 4
            
        elif condition.operator == "LEQ":
            self.code.append(f"LOAD {self.symbols.get_variable(condition.value1)}")
            self.code.append(f"SUB {self.symbols.get_variable(condition.value2)}")
            self.code.append(f"JNEG {jump_if_true}")
            self.code.append(f"JZERO {jump_if_true}")
            
            return linenum + 4
            
        elif condition.operator == "GEQ":
            self.code.append(f"LOAD {self.symbols.get_variable(condition.value1)}")
            self.code.append(f"SUB {self.symbols.get_variable(condition.value2)}")
            self.code.append(f"JPOS {jump_if_true}")
            self.code.append(f"JZERO {jump_if_true}")
            
            return linenum + 4
        
        elif condition.operator == "LT":
            self.code.append(f"LOAD {self.symbols.get_variable(condition.value1)}")
            self.code.append(f"SUB {self.symbols.get_variable(condition.value2)}")
            self.code.append(f"JNEG {jump_if_true}")
            
            return linenum + 3
        
        elif condition.operator == "GT":
            self.code.append(f"LOAD {self.symbols.get_variable(condition.value1)}")
            self.code.append(f"SUB {self.symbols.get_variable(condition.value2)}")
            self.code.append(f"JPOS {jump_if_true}")
            
            return linenum + 3
        