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
        # # arguments will be in the  first few memory cells starting with 1, before variables
        # # will appear in order of declaration
        # ! arguments need to be passed by reference, not by copying and restoring
        
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
    
        linenum = self.generate_commands(main.commands)
    
    
    def generate_commands(self, commands : nd.Commands):
        linenum = 0
        inner_code = []
        
        for comm in commands.commands:
            if type(comm) == nd.Assign:
                
                #? can't load the assigned variable here bacause it will immediately be overriden in the expression generation
                # inner_code.append(f"LOAD {self.symbols.get_variable(comm.variable.name)}")
                # linenum = linenum + 1;
                
                return_linenum, return_code = self.generate_expression(comm.assignment)
                inner_code += return_code
                linenum += return_linenum
                
                # store the calculated expression in the right variable
                #? this will always be a variable and not a constant, as you can't assign value to a constant
                inner_code.append(f"STORE {self.symbols.get_variable(comm.variable.name)}")
                linenum += 1
                
                
            elif type(comm) == nd.IfStatement:
                linenum, c = self.generate_ifstatement(comm)
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
                # you cannot read a constant so there's need for the same conditions as in WRITE
                # TODO you can read an array though
                inner_code.append(f"GET {self.symbols.get_variable(comm.variable.name)}")
                linenum += 1
                
            elif type(comm) == nd.Write:
                if isinstance(comm.value, nd.Identifier):
                    inner_code.append(f"PUT {self.symbols.get_variable(comm.value)}")
                    linenum += 1
                elif isinstance(comm.value, nd.Array):
                    pass
                else:
                    if self.symbols.is_declared(comm.value):
                        inner_code.append(f"PUT {self.symbols.get_const(comm.value)}")
                        linenum += 1
                    else:
                        self.symbols.add_const(comm.value)
                        inner_code.append(f"SET {comm.value}")
                        inner_code.append(f"STORE {self.symbols.get_const(comm.value)}")
                        inner_code.append(f"PUT {self.symbols.get_const(comm.value)}")
                    
                
        
        return linenum, inner_code
                
    
    def generate_ifstatement(self, ifstatement : nd.IfStatement):
        inner_code = list()
        linenum = 0
        
        # TODO optimize for unreachable code blocks
        # like if 1 > 2 
        
        
        #THIS IS (not anymore) ALL TRASH
        # if block should come first because if else doesn't exist there's nothing to jump to
        # wait no
        # in any case, there should be a jump to skip if, if the condition is false
        # though if there is an else block there would need to be a second jump to bypass if
        # if there's no else block the only jump is to bypass if or not
        # so if block should come first, so there's only a jump to skip if, and a jump to skip else after if was executed
        # I think? it might not have much significance at all
        # it's also possible to do either one first based on which code is shorter
        #? damn what a mess
        
        #* Expressions should definitely jump over to else, not if, because of use of conditions in other code blocks
        # as in, loops
        
        lines_if, code_if = self.generate_commands(ifstatement.commands)
        
        if ifstatement.else_commands is not None:
            lines_else, code_else = self.generate_commands(ifstatement.else_commands)
        else:
            lines_else = 0
            code_else = []
        
        # if the condition is true don't jump, if it's false jump right after if block
        lines_cond, code_cond = self.generate_condition(ifstatement.condition, 0, linenum + lines_if)
        
        
        inner_code += code_cond
        linenum += lines_cond
        inner_code += code_if
        linenum += lines_if
        inner_code.append(f"JUMP {linenum + lines_else}")
        linenum += 1
        inner_code += code_else
        linenum += lines_else
        
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
    
    def generate_expression(self, expression : nd.Expression):
        linenum = 0
        inner_code = []
        
        # TODO if both are numbers just calculate it
        
        
        
        # // I believe it's safe to directly append these lines to code
        # // as it seems to be illegal to use an expression in a condition
        # // I might change it to use inner_code to be consistent with other functions
        # nope, expressions can be invoked in generate_commands, which means that they must return their own code
        if expression.operator == "ADD":\
            
            if isinstance(expression.value1, nd.Identifier):
                inner_code.append(f"LOAD  {self.symbols.get_variable(expression.value1.name)}")
            elif isinstance(expression.value1, nd.Array):
                pass
            else:
                if self.symbols.is_declared(expression.value1):
                    inner_code.append(f"LOAD  {self.symbols.get_const(expression.value1)}")
                    linenum += 1
                else:
                    self.symbols.add_const(expression.value1)
                    inner_code.append(f"SET {expression.value1}")
                    inner_code.append(f"STORE {self.symbols.get_const(expression.value1)}")
                    # I *think* there's no need to load again afterwards because it stays in the accumulator
                    linenum += 2
                
            
            if isinstance(expression.value2, nd.Identifier):
                inner_code.append(f"ADD  {self.symbols.get_variable(expression.value2.name)}")
            elif isinstance(expression.value2, nd.Array):
                pass
            else:
                if self.symbols.is_declared(expression.value2):
                    inner_code.append(f"ADD  {self.symbols.get_const(expression.value2)}")
                    linenum += 1
                else:
                    self.symbols.add_const(expression.value2)
                    inner_code.append(f"SET {expression.value2}")
                    inner_code.append(f"STORE {self.symbols.get_const(expression.value2)}")
                    inner_code.append(f"ADD {self.symbols.get_const(expression.value2)}")
                    linenum += 3
                    
            
            
            #* I don't think it's necessary to store the result anywhere
            #* It will immediately get assigned to whichever variable right after returning from this function
            # returns result to 1
            # I assume the function that called this will do something with it
            # this will likely need to get optimized for not having consecutive stores and loads on the same register
            # inner_code.append("STORE 1")
            # linenum += 1
            
            return linenum, inner_code
        
        elif expression.operator == "SUB":
            if isinstance(expression.value1, nd.Identifier):
                inner_code.append(f"LOAD  {self.symbols.get_variable(expression.value1.name)}")
            else:
                inner_code.append(f"LOAD  {self.symbols.get_const(expression.value1)}")
                
            linenum += 1
            
            if isinstance(expression.value2, nd.Identifier):
                inner_code.append(f"SUB  {self.symbols.get_variable(expression.value2.name)}")
            else:
                inner_code.append(f"SUB  {self.symbols.get_const(expression.value2)}")
            linenum += 1
            
            # inner_code.append("STORE 1")
            # linenum += 1
            
            return linenum, inner_code
        
        elif expression.operator == "MUL":
            # self.multiplication()
            pass
        
        elif expression.operator == "DIV":
            # self.division()
            pass
        
        elif expression.operator == "MOD":
            # self.modulo()
            
            pass
        
    def generate_condition(self, condition : nd.Condition, jump_if_true, jump_if_false):
        # counter of lines added by this function
        linenum = 0
        
        # TODO optimize for already known conditions like 1 = 2
        
        # TODO make it work with arrays, variables and constants
        
        # TODO rewrite so the jumps are correct (not always to true)
        
        if condition.operator == "EQ":
            self.code.append(f"LOAD {self.symbols.get_variable(condition.value1)}")
            self.code.append(f"SUB {self.symbols.get_variable(condition.value2)}")
            self.code.append(f"JZERO {jump_if_true}")
            # should I include jumping if false?
            
            # this could technically be just return 3 but I'll leave it like this for if I change something again
            return linenum + 3
        
        elif condition.operator == "NEQ":
            self.code.append(f"LOAD {self.symbols.get_variable(condition.value1)}")
            self.code.append(f"SUB {self.symbols.get_variable(condition.value2)}")
            
            # if it's either positive or negative then the condition is true
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
        