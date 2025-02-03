from symbol_table import SymbolTable, Array, ArrayReference
from postprocessor import Postprocessor
from preprocessor import Preprocessor
import nodes as nd

class CodeGenerator:
    def __init__(self, tree):
        self.tree : nd.Program = tree
        self.symbols = SymbolTable()
        
        # list of strings 
        self.code = []
        
    
    def generate(self):
        preprocessor = Preprocessor()
        self.consts, self.procedures = preprocessor.preprocess(self.tree)
        
        
        for const in self.consts:
            self.symbols.add_const(const)
            self.code.append(f"SET {const}")
            self.code.append(f"STORE {self.symbols.get_const(const)}")
            
            
        div_code = []
        if "0_DIV" in self.procedures or "0_MOD" in self.procedures:
            div_code = self.division()
            self.symbols.add_procedure("0_DIV", len(self.code) + 1)
        mul_code = []
        if "0_MUL" in self.procedures:
            mul_code = self.multiplication()
            self.symbols.add_procedure("0_MUL", len(self.code) + len(div_code) + 1)
            
            
        self.offset = len(self.code) + len(div_code) + len(mul_code)
        
        code_procedures = []
        code_procedures = self.generate_procedures(self.tree.procedures)
        

        # initially skip all procedures and jump straight to main
        if len(code_procedures) + len(div_code) + len(mul_code)> 0:
            self.code.append(f"JUMP {len(code_procedures) + len(div_code) + len(mul_code) + 1}")
        self.code += div_code
        self.code += mul_code
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
        offset = self.offset + 1
        
        for proc in procedures.procedures:
            self.symbols.add_procedure(proc.proc_head.pid, offset)
            inner_code += self.generate_procedure(proc)
            offset = self.offset +  len(inner_code) + 1
        return inner_code
            
    
    #? distinct from generate_procedures()
    # that one is plural, this one is singular
    def generate_procedure(self, procedure : nd.Procedure):
        procedure_name = procedure.proc_head.pid
        # starts with one for easy distinguishing from 0main
        prefix = procedure_name + "_"
        
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
                    self.symbols.add_array(prefix + var.name, var.start, var.end)      
                else:
                    self.symbols.add_variable(prefix + var)
        
        inner_code = self.generate_commands(procedure.commands, prefix)[1]
        inner_code.append(f"RTRN {self.symbols.get_return(procedure_name)}")
        return inner_code
    
    def generate_main(self, main : nd.Main):
        prefix = "main_"
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
                                
                parameters : list = self.symbols.get_proc_arg(comm.pid)
                procedure_prefix = comm.pid + "_"
                if procedure_prefix == prefix:
                    raise Exception(f"Calling procedure {comm.pid} from within itself")
                
                
                if len(comm.args.arguments) == len(parameters):
                    for i in range(len(comm.args.arguments)):
                        if self.symbols.is_array(prefix + comm.args.arguments[i]) and not (isinstance(parameters[i], Array) or isinstance(parameters[i], ArrayReference)):
                            raise Exception(f"Passing an array ({prefix + comm.args.arguments[i]}) to a procedure as an argument which should not be an array ({parameters[i].name})")
                        elif isinstance(parameters[i], Array) or isinstance(parameters[i], ArrayReference) and not self.symbols.is_array(prefix + comm.args.arguments[i]):
                            raise Exception(f"Passing a variable ({prefix + comm.args.arguments[i]}) to a procedure as an argument that should be an array ({parameters[i].name})")
                        
                        
                        if self.symbols.is_reference(prefix + comm.args.arguments[i]):
                            inner_code.append(f"LOAD {self.symbols.get_variable(prefix + comm.args.arguments[i])}")
                        elif self.symbols.is_array_reference(prefix + comm.args.arguments[i]):
                            pass
                        elif self.symbols.is_array(prefix + comm.args.arguments[i]):
                            inner_code.append(f"SET {self.symbols.get_array_position(prefix + comm.args.arguments[i], 0)}")
                        else:                            
                            inner_code.append(f"SET {self.symbols.get_variable(prefix + comm.args.arguments[i])}")
                            self.symbols.mark_as_initialized(prefix + comm.args.arguments[i])
                        #? constants can't be passed to procedures
                        
                        inner_code.append(f"STORE {self.symbols.get_variable(parameters[i].name)}")
                    
                    # will get swapped to current line number in postprocessing
                    inner_code.append("SET ret")
                    inner_code.append(f"STORE {self.symbols.get_return(comm.pid)}")
                    inner_code.append(f"JUMP {comm.pid}")
                
            elif type(comm) == nd.Read:
                inner_code.append("GET 0")
                inner_code += self.store(comm.variable, prefix)
                linenum = len(inner_code)
                
            elif type(comm) == nd.Write:
                inner_code += self.load(comm.value, prefix)
                inner_code.append("PUT 0")
                linenum = len(inner_code)
                    
                
        
        return linenum, inner_code
                
    
    def generate_ifstatement(self, ifstatement : nd.IfStatement, prefix):
        inner_code = list()
        linenum = 0
        
        # TODO optimize for unreachable code blocks
        # like if 1 > 2 
        
        
        lines_if, code_if = self.generate_commands(ifstatement.commands, prefix)
        lines_if = len(code_if)
        
        if ifstatement.else_commands is not None:
            lines_else, code_else = self.generate_commands(ifstatement.else_commands, prefix)
            lines_else = len(code_else)
        else:
            lines_else = 0
            code_else = []
        
        # if the condition is true don't jump, if it's false jump right after if block
        lines_cond, code_cond = self.generate_condition(ifstatement.condition, lines_if + 1, False, prefix) 
        lines_cond = len(code_cond)
        
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
        lines_comm = len(code_comm)
        lines_cond, code_cond = self.generate_condition(whileloop.condition, lines_comm + 1, False, prefix)
        lines_cond = len(code_cond)

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
        lines_cond, code_cond = self.generate_condition(repeat.condition, 0 - lines_comm - 2, False, prefix)
        
        lines_comm = len(code_comm)
        lines_cond = len(code_cond)
        
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
            inner_code.append(f"LOAD {self.symbols.get_const(1)}")
            self.symbols.add_const(1)
            inner_code.append(f"STORE {self.symbols.get_const(1)}")
            linenum += 2
                    
        self.symbols.add_iterator(prefix + forloop.iterator)
        
        inner_code += self.load(forloop.end_value, prefix)
        linenum = len(inner_code)
                
        # store in memory so that it never changes with changes to the variable
        inner_code.append(f"STORE {self.symbols.get_iterator_condition(prefix + forloop.iterator)}")
        
        inner_code += self.load(forloop.start_value, prefix)
        linenum = len(inner_code)
        
        inner_code.append(f"STORE {self.symbols.get_iterator(prefix + forloop.iterator)}")
        linenum += 1
        
        linenum = len(inner_code)
        line_sub = linenum
        
        inner_code.append(f"SUB {self.symbols.get_iterator_condition(prefix + forloop.iterator)}")
        

        lines_comm, code_comm = self.generate_commands(forloop.commands, prefix)   
        lines_comm = len(code_comm)
        
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

            elif expression.value2 == 2:
                inner_code.append(f"LOAD {self.symbols.get_variable(prefix + expression.value1.name)}")
                inner_code.append(f"ADD 0")

            elif expression.value1 == 0 or expression.value2 == 0:
                inner_code.append(f"LOAD {self.symbols.get_const(0)}")

            elif expression.value1 == 1:
                inner_code += self.load(expression.value2)
            elif expression.value2 == 1:
                inner_code += self.load(expression.value1)
                
            elif expression.value1 == -1:
                inner_code += self.load(expression.value2)
                inner_code.append("STORE 1")
                inner_code.append("SUB 1")
                inner_code.append("SUB 1")
                
            elif expression.value2 == -1:
                inner_code += self.load(expression.value1)
                inner_code.append("STORE 1")
                inner_code.append("SUB 1")
                inner_code.append("SUB 1")
                
            # TODO this is the place for all multiplication optimizations
            
            else:
                #* really lengthy but necessary for handling negative numbers
                #* optimisation: check in preprocessing if this handling is needed at all

                
                inner_code += self.load(expression.value1, prefix)
                inner_code.append("STORE 3")

                
                return_code = self.load(expression.value2, prefix)

                inner_code.append(f"JZERO {8 + len(return_code)}")
                inner_code += return_code
                               
                inner_code.append("STORE 4")
                inner_code.append("JZERO 6")
                
                
                inner_code.append("SET ret")
                inner_code.append("STORE 9")
                inner_code.append("JUMP 0_MUL")                
                inner_code.append("LOAD 5")
                inner_code.append("JUMP 2")
                
                inner_code.append(f"LOAD {self.symbols.get_const(0)}")
                
            return len(inner_code), inner_code
            
        
        # TODO change SET to loading 0
        elif expression.operator == "DIV":
            if expression.value2 == 2:
                inner_code += self.load(expression.value1, prefix)
                inner_code.append("HALF")
            elif expression.value1 == 0 or expression.value2 == 0:
                inner_code.append(f"LOAD {self.symbols.get_const(0)}")

            else:
                inner_code += self.load(expression.value1, prefix)
                inner_code.append("STORE 3")
                inner_code += self.load(expression.value2, prefix)
                inner_code.append("STORE 4")
                
                inner_code.append("SET ret")
                inner_code.append("STORE 9")
                inner_code.append("JUMP 0_DIV")
                
                inner_code.append("LOAD 5")
            
            return len(inner_code), inner_code
        
        elif expression.operator == "MOD":
            if expression.value1 == 0 or expression.value2 == 0:
                inner_code.append(f"LOAD {self.symbols.get_const(0)}")
            
            else:
                inner_code += self.load(expression.value1, prefix)
                inner_code.append("STORE 3")
                inner_code += self.load(expression.value2, prefix)
                inner_code.append("STORE 4")
                
                inner_code.append("SET ret")
                inner_code.append("STORE 9")
                inner_code.append("JUMP 0_DIV")
                
                inner_code.append("LOAD 3")
                
            return len(inner_code), inner_code
        
    def generate_condition(self, condition : nd.Condition, jump, mode : bool, prefix):
        # counter of lines added by this function
        linenum = 0
        inner_code = []
        
        # TODO optimize for already known conditions like 1 = 2
        
        
        
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
                if self.symbols.is_array(prefix + var.name):
                    raise Exception(f"Trying to assign value to array {prefix + var.name} without specifying index")
                
                if not self.symbols.is_initialized(prefix + var.name):
                    raise Exception(f"Using an uninitialized variable {prefix + var.name}")
                
                inner_code.append(f"LOAD {self.symbols.get_variable(prefix + var.name)}")
        elif isinstance(var, nd.ArrayPosition):
            if self.symbols.is_array_reference(prefix + var.name):
                if isinstance(var.position, int):
                    inner_code.append(f"SET {var.position}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + var.name)}")
                    inner_code.append(f"LOADI 0")
            
                else:
                    inner_code.append(f"LOAD {self.symbols.get_variable(prefix + var.name)}")
                    if self.symbols.is_reference(prefix + var.position):
                        inner_code.append(f"ADDI {self.symbols.get_variable(prefix + var.position)}")
                    else:
                        if not self.symbols.is_initialized(prefix + var.position):
                            raise Exception(f"Using an uninitialized variable {prefix + var.position}")
                        
                        inner_code.append(f"ADD {self.symbols.get_variable(prefix + var.position)}")
                    inner_code.append("LOADI 0")
            else:    
                if isinstance(var.position, int):
                    inner_code.append(f"LOAD {self.symbols.get_array_position(prefix + var.name, var.position)}")
                else:
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + var.name, 0)}")
                    
                    if self.symbols.is_reference(prefix + var.position):
                        inner_code.append(f"ADDI {self.symbols.get_variable(prefix + var.position)}")
                    else:
                        if not (self.symbols.is_initialized(prefix + var.position)):
                            raise Exception(f"Using an uninitialized variable {prefix + var.position}")       
                             
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
            inner_code.append("STORE 1")
            inner_code += self.load(var2, prefix)
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
            if self.symbols.is_array_reference(prefix + var.name):
                if isinstance(var.position, int):
                    inner_code.append("STORE 1")
                    inner_code.append(f"SET {var.position}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + var.name)}")
                    inner_code.append("STORE 2")
                    inner_code.append("LOAD 1")
                    inner_code.append("STOREI 2")
                    
                else:
                    inner_code.append("STORE 1")
                    inner_code.append(f"LOAD {self.symbols.get_variable(prefix + var.name)}")
                    
                    if self.symbols.is_reference(prefix + var.position):
                        inner_code.append(f"ADDI {self.symbols.get_variable(prefix + var.position)}")
                    else:
                        inner_code.append(f"ADD {self.symbols.get_variable(prefix + var.position)}")
                    
                    inner_code.append("STORE 2")
                    inner_code.append("LOAD 1")
                    inner_code.append("STOREI 2")
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
                raise Exception(f"Attempting to modify iterator {prefix + var.name}")
            else:
                inner_code.append(f"STORE {self.symbols.get_variable(prefix + var.name)}")
                self.symbols.mark_as_initialized(prefix + var.name)
            
        return inner_code
                           
    def division(self):
        inner_code = []
        
        if not self.symbols.is_declared(1):
            inner_code.append(f"LOAD {self.symbols.get_const(1)}")
            self.symbols.add_const(1)
            inner_code.append(f"STORE {self.symbols.get_const(1)}")
        
        
        inner_code.append(f"LOAD {self.symbols.get_const(0)}")
        inner_code.append("STORE 5")
        inner_code.append("STORE 7")
        inner_code.append("STORE 8")
        
        # inner_code += self.load(var1, prefix)
        # inner_code.append("STORE 3")
        inner_code.append("LOAD 3")
        inner_code.append("JZERO 62") #TODO
        inner_code.append("JPOS 6")
        inner_code.append("SUB 3") #flip the sign
        inner_code.append("SUB 3")
        inner_code.append("STORE 3")
        inner_code.append(f"LOAD {self.symbols.get_const(1)}")
        inner_code.append("STORE 7") #flag if product is positive or negative
        
        
        # inner_code += self.load(var2, prefix)
        # inner_code.append("STORE 4")
        inner_code.append("LOAD 4")
        inner_code.append("STORE 6")
        inner_code.append("JZERO 53") #TODO
        inner_code.append("JPOS 9")
        inner_code.append("SUB 4")
        inner_code.append("SUB 4")
        inner_code.append("STORE 4")
        inner_code.append("STORE 6") #keeps original divisor for future reference
        inner_code.append(f"LOAD {self.symbols.get_const(1)}") #SET 1
        inner_code.append("STORE 8") #flag if divisor is negative
        inner_code.append("SUB 7")
        inner_code.append("STORE 7")
    
        
        
        inner_code.append("LOAD 4")
        inner_code.append("ADD 0")
        inner_code.append("STORE 4")
        inner_code.append("SUB 3")
        inner_code.append("JNEG -4")
        inner_code.append("JZERO 4")
        inner_code.append("LOAD 4")
        inner_code.append("HALF")
        inner_code.append("STORE 4")
        
        inner_code.append("LOAD 3")
        inner_code.append("SUB 4")
        inner_code.append("JNEG 5")
        inner_code.append("STORE 3")
        inner_code.append("LOAD 5")
        inner_code.append(f"ADD {self.symbols.get_const(1)}")
        inner_code.append("STORE 5")
        inner_code.append("LOAD 4")
        inner_code.append("HALF")
        inner_code.append("STORE 4")
        inner_code.append("SUB 6")
        inner_code.append("JNEG 5")
        inner_code.append("LOAD 5")
        inner_code.append("ADD 0")
        inner_code.append("STORE 5")
        inner_code.append("JUMP -15")
        
        inner_code.append("LOAD 7") #if a*b<0
        inner_code.append("JZERO 10")
        inner_code.append("LOAD 5") #flip the sign of the result
        inner_code.append("SUB 5")
        inner_code.append("SUB 5")
        inner_code.append("STORE 5")
        inner_code.append("LOAD 3") #if a%b=0
        inner_code.append("JZERO 4")
        inner_code.append("LOAD 5")
        inner_code.append(f"SUB {self.symbols.get_const(1)}")
        inner_code.append("STORE 5")
        
        inner_code.append("LOAD 8")
        inner_code.append("JZERO 5")
        inner_code.append("LOAD 3")
        inner_code.append("SUB 3")
        inner_code.append("SUB 3")
        inner_code.append("STORE 3")
        
        inner_code.append("JUMP 4")
        
        inner_code.append(f"LOAD {self.symbols.get_const(0)}")
        inner_code.append("STORE 3")
        inner_code.append("STORE 5")
        
        inner_code.append("RTRN 9")
        
        return inner_code
    
    def multiplication(self):
        inner_code = []
        
        inner_code.append(f"LOAD {self.symbols.get_const(0)}")
        inner_code.append("STORE 5")
        inner_code.append("STORE 6") #sign flag
        
        inner_code.append("LOAD 3")
        inner_code.append("JPOS 6")
        inner_code.append("SUB 3")
        inner_code.append("SUB 3")
        inner_code.append("STORE 3")
        inner_code.append(f"LOAD {self.symbols.get_const(1)}") #negative flag
        inner_code.append("STORE 6")
        
        inner_code.append("LOAD 4")
        inner_code.append("JPOS 7")
        inner_code.append("SUB 4") #flip the sign
        inner_code.append("SUB 4")
        inner_code.append("STORE 4")
        inner_code.append(f"LOAD {self.symbols.get_const(1)}") #if flag was 0 it will be 1, if it was 1 it will be 0
        inner_code.append("SUB 6")
        inner_code.append("STORE 6")
        
        inner_code.append("LOAD 3")
        inner_code.append("HALF")
        inner_code.append("ADD 0")
        inner_code.append("SUB 3")
        inner_code.append("JZERO 3")
        inner_code.append("LOAD 4")
        inner_code.append("STORE 5")
        
        inner_code.append("LOAD 4")                
        inner_code.append("ADD 0")
        inner_code.append("STORE 4")
        inner_code.append("LOAD 3")
        inner_code.append("HALF")
        inner_code.append("JZERO 10")
        inner_code.append("STORE 3")
        inner_code.append("HALF")
        inner_code.append("ADD 0")
        inner_code.append("SUB 3")
        inner_code.append("JZERO -10")
        inner_code.append("LOAD 4")
        inner_code.append("ADD 5")
        inner_code.append("STORE 5")
        inner_code.append("JUMP -14")

        inner_code.append("LOAD 6")
        inner_code.append("JZERO 5")
        inner_code.append("LOAD 5")
        inner_code.append("SUB 5")
        inner_code.append("SUB 5")
        inner_code.append("JUMP 2")
        
        inner_code.append("RTRN 9")
        
        return inner_code