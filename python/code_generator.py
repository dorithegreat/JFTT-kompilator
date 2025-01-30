from symbol_table import SymbolTable
from postprocessor import Postprocessor
import nodes as nd

class CodeGenerator:
    def __init__(self, tree):
        self.tree : nd.Program = tree
        self.symbols = SymbolTable()
        
        # list of strings 
        self.code = []
        
    
    def generate(self):
        code_procedures = self.generate_procedures(self.tree.procedures)
        
        # initially skip all procedures and jump straight to main
        self.code.append(f"JUMP {len(code_procedures) + 1}")
        self.code += code_procedures
        
        # for backwards compatiility with an earlier version of this project some functions track the amount of lines they've added as linenum
        # this is always exactly equal to the length of code generated within that function
        linenum_after_main, code_main = self.generate_main(self.tree.main)
        self.code += code_main
        self.code.append("HALT")
        
        postprocessor = Postprocessor(self.symbols)
        postprocessor.postprocess(self.code)
    
    
    def generate_procedures(self, procedures : nd.Procedures):
        inner_code = []
        offset = 1
        
        for proc in procedures.procedures:
            self.symbols.add_procedure(proc.proc_head.pid, offset)
            inner_code += self.generate_procedure(proc)
            offset = len(inner_code) + 1
        return inner_code
            
    
    #? distinct from generate_procedures()
    # that one is plural, this one is singular
    def generate_procedure(self, procedure : nd.Procedure):
        procedure_name = procedure.proc_head.pid
        # starts with one for easy distinguishing from 0main
        prefix = "1" + procedure_name + "_"
        
        # add arguments
        for var in procedure.proc_head.args_decl.arguments:
            if isinstance(var, nd.Array):
                self.symbols.add_array_reference(prefix + var.name)
                self.symbols.add_proc_arg(procedure_name, prefix + var.name)
            else:
                self.symbols.add_reference(prefix + var)
                self.symbols.add_proc_arg(procedure_name, prefix + var)
                
        # add declared variables
        #* same as arguments but not by reference
        if procedure.declaration is not None:
            for var in procedure.declaration.declarations:
                if isinstance(var, nd.Array):
                    pass        
                else:
                    self.symbols.add_variable(prefix + var)
        
        inner_code = self.generate_commands(procedure.commands, prefix)[1]
        inner_code.append(f"RTRN {self.symbols.get_return(procedure_name)}")
        return inner_code
    
    def generate_main(self, main : nd.Main):
        prefix = "0main_"
        for var in main.declarations.declarations:
            if (isinstance(var, nd.Array)):
                self.symbols.add_array(prefix + var.name, var.start, var.end)
            else:
                self.symbols.add_variable(prefix + var)
    
        linenum, inner_code = self.generate_commands(main.commands, prefix)
        return linenum, inner_code
    
    
    def generate_commands(self, commands : nd.Commands, prefix):
        linenum = 0
        inner_code = []
        
        for comm in commands.commands:
            if type(comm) == nd.Assign:
                
                return_linenum, return_code = self.generate_expression(comm.assignment, prefix)
                inner_code += return_code
                linenum += return_linenum
                
                return_code = self.store(comm.variable, prefix)
                inner_code += return_code
                linenum += len(return_code)
                
                
            elif type(comm) == nd.IfStatement:
                l, c = self.generate_ifstatement(comm, prefix)
                inner_code += c
                linenum += l
            elif type(comm) == nd.WhileLoop:
                l, c = self.generate_while(comm, prefix)
                inner_code += c
                linenum += l
            elif type(comm) == nd.RepeatUntil:
                l, c = self.generate_repeat_until(comm, prefix)
                inner_code += c
                linenum += l
            elif type(comm) == nd.ForTo:
                l, c = self.generate_for(comm, prefix)
                inner_code += c
                linenum += l
            elif type(comm) == nd.ForDownto:
                l, c = self.generate_for(comm, prefix)
                inner_code += c
                linenum += l
            elif type(comm) == nd.ProcCall:
                # TODO only allow calling procedures defined earlier
                                
                parameters : list = self.symbols.get_proc_arg(comm.pid)
                procedure_prefix = "1" + comm.pid + "_"
                
                if len(comm.args.arguments) == len(parameters):
                    for i in range(len(comm.args.arguments)):
                        if self.symbols.is_reference(prefix + comm.args.arguments[i]):
                            inner_code.append(f"LOAD {self.symbols.get_variable(prefix + comm.args.arguments[i])}")
                        elif self.symbols.is_array_reference(prefix + comm.args.arguments[i]):
                            pass
                        elif isinstance(comm.args.arguments[i], nd.Array):
                            inner_code.append(f"SET {self.symbols.get_array_position(prefix + comm.args.arguments[i].name, 0)}")
                        else:                            
                            inner_code.append(f"SET {self.symbols.get_variable(prefix + comm.args.arguments[i])}")

                        inner_code.append(f"STORE {self.symbols.get_variable(parameters[i].name)}")
                    
                    # will get swapped to current line number in postprocessing
                    inner_code.append("SET ret")
                    inner_code.append(f"STORE {self.symbols.get_return(comm.pid)}")
                    inner_code.append(f"JUMP {comm.pid}")
                
            elif type(comm) == nd.Read:
                # you cannot read a constant so there's need for the same conditions as in WRITE
                # TODO you can read an array though
                if isinstance(comm.variable, nd.ArrayPosition):
                    inner_code.append(f"GET {self.symbols.get_array_position(prefix + comm.variable.name, comm.variable.position)}")
                    linenum += 1
                else:
                    inner_code.append(f"GET {self.symbols.get_variable(prefix + comm.variable.name)}")
                    linenum += 1
                
            elif type(comm) == nd.Write:
                if isinstance(comm.value, nd.Identifier):
                    inner_code.append(f"PUT {self.symbols.get_variable(prefix + comm.value.name)}")
                    linenum += 1
                elif isinstance(comm.value, nd.ArrayPosition):
                    if isinstance(comm.value.position, int):
                        inner_code.append(f"PUT {self.symbols.get_array_position(prefix + comm.value.name, comm.value.position)}")
                        linenum += 1
                    else:
                        
                        #? set the accumulator to the index of the start of the array
                        # it is done by requesting the address of the first index of the array, in a roundabout way
                        inner_code.append(f"SET {self.symbols.get_array_position(prefix + comm.value.name, 0)}")
                        # add to it whatever value is hidden under the variable used as index
                        inner_code.append(f"ADD {self.symbols.get_variable(prefix + comm.value.position)}")
                        # put it down for easier access
                        inner_code.append(f"STORE 1")
                        # load from memory cell with index equal to the value in 1
                        inner_code.append(f"LOADI 1")
                        inner_code.append(f"PUT 0")
                        
                        linenum += 5
                else:
                    if self.symbols.is_declared(comm.value):
                        inner_code.append(f"PUT {self.symbols.get_const(comm.value)}")
                        linenum += 1
                    else:
                        self.symbols.add_const(comm.value)
                        inner_code.append(f"SET {comm.value}")
                        inner_code.append(f"STORE {self.symbols.get_const(comm.value)}")
                        inner_code.append(f"PUT {self.symbols.get_const(comm.value)}")
                        linenum += 3
                    
                
        
        return linenum, inner_code
                
    
    def generate_ifstatement(self, ifstatement : nd.IfStatement, prefix):
        inner_code = list()
        linenum = 0
        
        # TODO optimize for unreachable code blocks
        # like if 1 > 2 
        
        
        lines_if, code_if = self.generate_commands(ifstatement.commands, prefix)
        
        if ifstatement.else_commands is not None:
            lines_else, code_else = self.generate_commands(ifstatement.else_commands, prefix)
        else:
            lines_else = 0
            code_else = []
        
        # if the condition is true don't jump, if it's false jump right after if block
        lines_cond, code_cond = self.generate_condition(ifstatement.condition, lines_if + 1, False, prefix) 
        
        
        inner_code += code_cond
        linenum += lines_cond
        inner_code += code_if
        linenum += lines_if
        inner_code.append(f"JUMP {lines_else + 1}")
        linenum += 1
        inner_code += code_else
        linenum += lines_else
        
        return linenum, inner_code
            
    def generate_while(self, whileloop : nd.WhileLoop, prefix):
        linenum = 0
        inner_code = []
        
        lines_comm, code_comm = self.generate_commands(whileloop.commands, prefix)
        lines_cond, code_cond = self.generate_condition(whileloop.condition, lines_comm + 1, False, prefix)
        

        inner_code += code_cond
        linenum += lines_cond
        inner_code += code_comm
        linenum += lines_comm

        inner_code.append(f"JUMP {0 - linenum}")
        linenum += 1
        
        return linenum, inner_code
        
    def generate_repeat_until(self, repeat : nd.RepeatUntil, prefix):
        linenum = 0
        inner_code = []
        
        lines_comm, code_comm = self.generate_commands(repeat.commands, prefix)
        lines_cond, code_cond = self.generate_condition(repeat.condition, 0 - lines_comm, False, prefix)
        
        #? this is repeat until - commands go first and only afterwards is the condition checked
        inner_code += code_comm
        linenum += lines_comm
        inner_code += code_cond
        linenum += lines_cond

        
        return linenum, inner_code
        
    def generate_for(self, forloop, prefix):
        inner_code = []
        linenum = 0 
        
        if not self.symbols.is_declared(1):
            inner_code.append("SET 1")
            self.symbols.add_const(1)
            inner_code.append(f"STORE {self.symbols.get_const(1)}")
            linenum += 2
                    
        # TODO make sure iterators can't be modified within the loop
        self.symbols.add_iterator(prefix + forloop.iterator)
        
        inner_code += self.load(forloop.end_value, prefix)
        linenum = len(inner_code)
                
        # store in memory so that it never changes with changes to the variable
        inner_code.append(f"STORE {self.symbols.get_iterator_condition(prefix + forloop.iterator)}")
        
        if isinstance(forloop.start_value, nd.Identifier):
            inner_code.append(f"LOAD  {self.symbols.get_variable(prefix + forloop.start_value.name)}")
            linenum += 1
        elif isinstance(forloop.start_value, nd.ArrayPosition):
            if isinstance(forloop.start_value.position, int):
                inner_code.append(f"LOAD {self.symbols.get_array_position(prefix + forloop.start_value.name, forloop.start_value.position)}")
                linenum += 1
            else:
                inner_code.append(f"SET {self.symbols.get_array_position(prefix + forloop.start_value.name, self.symbols.get_array_beginning(prefix + forloop.start_value.name))}")
                inner_code.append(f"ADD {self.symbols.get_variable(prefix + forloop.start_value.position)}")
                inner_code.append("STORE 1")
                inner_code.append(f"LOADI 1")
                
                linenum += 4
                            
        else:
            if self.symbols.is_declared(forloop.start_value):
                inner_code.append(f"LOAD  {self.symbols.get_const(forloop.start_value)}")
                linenum += 1
            else:
                self.symbols.add_const(forloop.start_value)
                inner_code.append(f"SET {forloop.start_value}")
                inner_code.append(f"STORE {self.symbols.get_const(forloop.start_value)}")
                # I *think* there's no need to load again afterwards because it stays in the accumulator
                linenum += 2
            
        inner_code.append(f"STORE {self.symbols.get_iterator(prefix + forloop.iterator)}")
        linenum += 1
        
        line_sub = linenum
        
        inner_code.append(f"SUB {self.symbols.get_iterator_condition(prefix + forloop.iterator)}")
        

        lines_comm, code_comm = self.generate_commands(forloop.commands, prefix)   
        
        if isinstance(forloop, nd.ForTo):
            inner_code.append(f"JPOS {lines_comm + 5}")
            linenum += 1
        else:
            inner_code.append(f"JNEG {lines_comm + 5}")
            linenum += 1
        
        # inner_code.append(f"JZERO {lines_comm + 5}")
        
        inner_code += code_comm
        linenum += lines_comm
        
        inner_code.append(f"LOAD {self.symbols.get_iterator(prefix + forloop.iterator)}")
        if isinstance(forloop, nd.ForDownto):
            inner_code.append(f"SUB {self.symbols.get_const(1)}")
        else:
            inner_code.append(f"ADD {self.symbols.get_const(1)}")
        
        inner_code.append(f"STORE {self.symbols.get_iterator(prefix + forloop.iterator)}")
        linenum += 3
        
        # there is no checking if the result is 0 because the jump leads to JZERO to skip the loop
        # at lest, it should
        inner_code.append(f"JUMP {line_sub - linenum - 1}")
        linenum += 1
        
        self.symbols.dealocate_iterator(prefix + forloop.iterator)
        return linenum, inner_code
        
    
    def generate_expression(self, expression : nd.Expression, prefix):
        linenum = 0
        inner_code = []
        
        # TODO if both are numbers just calculate it
        
        if expression.operator is None:
            inner_code += self.load(expression.value1, prefix)
            linenum = len(inner_code)
            return linenum, inner_code            
        
        if expression.operator == "ADD":
            inner_code += self.load_and_do_something(expression.value1, expression.value2, "ADD", prefix)
            linenum = len(inner_code)
            return linenum, inner_code
        
        
        elif expression.operator == "SUB":
            inner_code += self.load_and_do_something(expression.value1, expression.value2, "SUB", prefix)
            linenum = len(inner_code)
            return linenum, inner_code
        
        elif expression.operator == "MUL":
            # TODO implement for all numbers
            if expression.value1 == 2:
                inner_code.append(f"LOAD {self.symbols.get_variable(prefix + expression.value2.name)}")
                inner_code.append(f"ADD {self.symbols.get_variable(prefix + expression.value2.name)}")
                linenum += 2
                return linenum, inner_code
        
        elif expression.operator == "DIV":
            if expression.value2 == 2:
                inner_code.append(f"LOAD {self.symbols.get_variable(prefix + expression.value1.name)}")
                inner_code.append("HALF")
                linenum += 2
                return linenum, inner_code
        
        elif expression.operator == "MOD":
            # self.modulo()
            
            pass
        
    def generate_condition(self, condition : nd.Condition, jump, mode : bool, prefix):
        # counter of lines added by this function
        linenum = 0
        inner_code = []
        
        # TODO optimize for already known conditions like 1 = 2
        
        # TODO make it work with arrays, variables and constants
        
        # TODO rewrite so the jumps are correct (not always to true)
        
        
        inner_code += self.load_and_do_something(condition.value1, condition.value2, "SUB", prefix)
        linenum += len(inner_code)
        
        if jump < 0:
            jump -= linenum
        
        if condition.operator == "EQ":
                               
            if mode == True:
                inner_code.append(f"JZERO {jump + 1}")
                linenum += 1
            else:
                inner_code.append(f"JNEG {jump + 2}")
                inner_code.append(f"JPOS {jump + 1}")
                linenum += 2
                
            return linenum, inner_code
                
        
        elif condition.operator == "NEQ":
            #* literally just the opposite of the above
            if mode == False:
                inner_code.append(f"JZERO {jump + 1}")
                linenum += 1
            else:
                inner_code.append(f"JNEG {jump + 2}")
                inner_code.append(f"JPOS {jump + 1}")
                linenum += 2
                
            return linenum, inner_code
            
        elif condition.operator == "LEQ":
            if mode == True:
                inner_code.append(f"JNEG {jump +2 }")
                inner_code.append(f"JZERO {jump + 1}")
                linenum += 2
            else:
                inner_code.append(f"JPOS {jump + 1}")
                linenum += 1
                
            return linenum, inner_code
            
        elif condition.operator == "GEQ":
            if mode == True:
                inner_code.append(f"JZERO {jump + 2}")
                inner_code.append(f"JPOS {jump + 1}")
                linenum += 2
            else:
                inner_code.append(f"JNEG {jump + 1}")
                linenum += 1
                
            return linenum, inner_code
        
        elif condition.operator == "LT":
            if mode == False:
                inner_code.append(f"JZERO {jump +2}")
                inner_code.append(f"JPOS {jump + 1}")
                linenum += 2
            else:
                inner_code.append(f"JNEG {jump + 1}")
                linenum += 1
                
            return linenum, inner_code
        
        elif condition.operator == "GT":
            if mode == True:
                inner_code.append(f"JPOS {jump + 1}")
                linenum += 1
            else:
                inner_code.append(f"JNEG {jump + 2}")
                inner_code.append(f"JZERO {jump + 1}")
                linenum += 2
                
                
            return linenum, inner_code
            
        
    def load(self, var, prefix):
        inner_code = []
        

        if isinstance(var, nd.Identifier):
            if self.symbols.is_reference(prefix + var.name):
                inner_code.append(f"LOADI {self.symbols.get_variable(prefix + var.name)}")
            else:
                inner_code.append(f"LOAD {self.symbols.get_variable(prefix + var.name)}")
        elif isinstance(var, nd.ArrayPosition):
            if isinstance(var.position, int):
                inner_code.append(f"LOAD {self.symbols.get_array_position(prefix + var.name, var.position)}")
            else:
                inner_code.append(f"SET {self.symbols.get_array_position(prefix + var.name, 0)}")
                inner_code.append(f"ADD {self.symbols.get_variable(prefix + var.position)}")
                inner_code.append(f"LOADI 0")
        else:
            if self.symbols.is_declared(var):
                inner_code.append(f"LOAD {self.symbols.get_const(var)}")
            else:
                self.symbols.add_const(var)
                inner_code.append(f"SET {var}")
                inner_code.append(f"STORE {self.symbols.get_const(var)}")
            
                    
        return inner_code
                
            

    def load_and_do_something(self, var1, var2, something, prefix):
        inner_code = []
        
        
        # it's more efficient to load the problematic array positions first
        if something == "ADD" and isinstance(var2, nd.ArrayPosition) and not isinstance(var1, nd.ArrayPosition):
            var1, var2 = var2, var1
        
        inner_code += self.load(var1, prefix)
        
        # TODO this is the place for all loading-related optimisations 
        

            

        if isinstance(var2, nd.Identifier):
            if self.symbols.is_reference(prefix + var2.name):
                if something == "ADD":
                    something = "ADDI"
                elif something == "SUB":
                    something = "SUBI"
                    
                inner_code.append(f"{something} {self.symbols.get_variable(prefix + var2.name)}")
            else:
                inner_code.append(f"{something} {self.symbols.get_variable(prefix + var2.name)}")
        elif isinstance(var2, nd.ArrayPosition):
            if isinstance(var2.position, int):
                inner_code.append(f"{something} {self.symbols.get_array_position(prefix + var2.name, var2.position)}")
            else:
                #* this looks awfully inefficient
                inner_code.append("STORE 1")
                inner_code.append(f"SET {self.symbols.get_array_position(prefix + var2.name,0)}")
                inner_code.append(f"ADD {self.symbols.get_variable(prefix + var2.position)}")
                inner_code.append("LOADI 0")
                inner_code.append("STORE 2")
                inner_code.append("LOAD 1")
                inner_code.append(f"{something} 2")
        else:
            if self.symbols.is_declared(var2):
                inner_code.append(f"{something} {self.symbols.get_const(var2)}")
            else:
                self.symbols.add_const(var2)
                inner_code.append("STORE 1")
                inner_code.append(f"SET {var2}")
                inner_code.append(f"STORE {self.symbols.get_const(var2)}")
                inner_code.append(f"LOAD 1")
                inner_code.append(f"{something} {self.symbols.get_const(var2)}")
                
        return inner_code
    
    def store(self, var, prefix):
        inner_code = []


            
        if isinstance(var, nd.ArrayPosition):
            if self.symbols.is_array_reference(var):
                pass
            else: 
                if isinstance(var.position, int):
                    inner_code.append(f"STORE {self.symbols.get_array_position(prefix + var.name, var.position)}")
                else:
                    inner_code.append("STORE 1")
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + var.name, 0)}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + var.position)}")
                    inner_code.append("STORE 2")
                    inner_code.append("LOAD 1")
                    inner_code.append("STOREI 2")
            
        else:
            if self.symbols.is_reference(prefix + var.name):
                inner_code.append(f"STOREI {self.symbols.get_variable(prefix + var.name)}")
            elif self.symbols.is_iterator(prefix + var.name):
                raise Exception("Attempting to modify iterator")
            else:
                inner_code.append(f"STORE {self.symbols.get_variable(prefix + var.name)}")
            
        return inner_code
                           