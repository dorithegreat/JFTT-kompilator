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
        
        linenum_after_main, code_main = self.generate_main(self.tree.main)
        self.code += code_main
        self.code.append("HALT")
    
    
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
        
    
    def generate_main(self, main : nd.Main):
        # TODO if I leave it like this no variable name can repeat between main and the procedures
        # I should probably reset symbol table after every procedure
        # actually I should't, the procedures will also get called later
        # in that case I should probably prepend the procedure name to the variable name in the symbol table
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
                
                #? can't load the assigned variable here bacause it will immediately be overriden in the expression generation
                # inner_code.append(f"LOAD {self.symbols.get_variable(comm.variable.name)}")
                # linenum = linenum + 1;
                
                return_linenum, return_code = self.generate_expression(comm.assignment, prefix)
                inner_code += return_code
                linenum += return_linenum
                
                # store the calculated expression in the right variable
                #? this will always be a variable and not a constant, as you can't assign value to a constant
                if isinstance(comm.variable, nd.ArrayPosition):
                    if isinstance(comm.variable.position, int):
                        inner_code.append(f"STORE {self.symbols.get_array_position(prefix + comm.variable.name, comm.variable.position)}")
                        linenum += 1
                    else:
                        inner_code.append("STORE 1")
                        inner_code.append(f"SET {self.symbols.get_array_position(prefix + comm.variable.name, self.symbols.get_array_beginning(prefix + comm.variable.name))}")
                        inner_code.append(f"ADD {self.symbols.get_variable(prefix + comm.variable.position)}")
                        inner_code.append("STORE 2")
                        inner_code.append("LOAD 1")
                        inner_code.append("STOREI 2")
                        linenum += 6
                    
                else:
                    inner_code.append(f"STORE {self.symbols.get_variable(prefix + comm.variable.name)}")
                    linenum += 1
                
                
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
                pass
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
                        inner_code.append(f"SET {self.symbols.get_array_position(prefix + comm.value.name, self.symbols.get_array_beginning(prefix + comm.value.name))}")
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
        
        if isinstance(forloop.end_value, nd.Identifier):
            inner_code.append(f"LOAD {self.symbols.get_variable(prefix + forloop.end_value.name)}")
            inner_code.append(f"STORE {self.symbols.get_iterator_condition(prefix + forloop.iterator)}")
            linenum += 2
        elif isinstance(forloop.end_value, nd.ArrayPosition):
            if isinstance(forloop.end_value.position, int):
                inner_code.append(f"LOAD {self.symbols.get_array_position(prefix + forloop.end_value.name, forloop.end_value.position)}")
                inner_code.append(f"STORE {self.symbols.get_iterator_condition(prefix + forloop.iterator)}")
                linenum += 2
                
            else:
                inner_code.append(f"SET {self.symbols.get_array_position(prefix + forloop.end_value.name, self.symbols.get_array_beginning(prefix + forloop.end_value.name))}")
                inner_code.append(f"ADD {self.symbols.get_variable(prefix + forloop.end_value.position)}")
                inner_code.append(f"LOADI 0")
                inner_code.append(f"STORE {self.symbols.get_iterator_condition(prefix + forloop.iterator)}")
                linenum += 4
        else:
            if self.symbols.is_declared(forloop.end_value):
                inner_code.append(f"LOAD {self.symbols.get_const(forloop.end_value)}")
                inner_code.append(f"STORE {self.symbols.get_iterator_condition(prefix + forloop.iterator)}")
                linenum += 2
                
            else:
                self.symbols.add_const(forloop.end_value)
                inner_code.append(f"SET {forloop.end_value}")
                inner_code.append(f"STORE {self.symbols.get_const(forloop.end_value)}")
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
        
        #TODO make sure these numbers are correct
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
            if isinstance(expression.value1, nd.Identifier):
                inner_code.append(f"LOAD  {self.symbols.get_variable(prefix + expression.value1.name)}")
                linenum += 1
            elif isinstance(expression.value1, nd.ArrayPosition):
                if isinstance(expression.value1.position, int):
                    inner_code.append(f"LOAD {self.symbols.get_array_position(prefix + expression.value1.name, expression.value1.position)}")
                    linenum += 1
                else:
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + expression.value1.name, self.symbols.get_array_beginning(prefix + expression.value1.name))}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + expression.value1.position)}")
                    inner_code.append("STORE 1")
                    inner_code.append(f"LOADI 1")
                    
                    linenum += 4
                
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
                    
            return linenum, inner_code            
        
        if expression.operator == "ADD":
            
            if isinstance(expression.value1, nd.Identifier):
                inner_code.append(f"LOAD  {self.symbols.get_variable(prefix + expression.value1.name)}")
                linenum += 1
            elif isinstance(expression.value1, nd.ArrayPosition):
                if isinstance(expression.value1.position, int):
                    inner_code.append(f"LOAD {self.symbols.get_array_position(prefix + expression.value1.name, expression.value1.position)}")
                    linenum += 1
                else:
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + expression.value1.name, self.symbols.get_array_beginning(prefix + expression.value1.name))}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + expression.value1.position)}")
                    inner_code.append("STORE 1")
                    inner_code.append(f"LOADI 1")
                    
                    linenum += 4
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
                inner_code.append(f"ADD  {self.symbols.get_variable(prefix + expression.value2.name)}")
                linenum += 1
            elif isinstance(expression.value2, nd.ArrayPosition):
                if isinstance(expression.value2.position, int):
                    inner_code.append(f"ADD {self.symbols.get_array_position(prefix + expression.value2.name, expression.value2.position)}")
                    linenum += 1
                    
                else:
                    inner_code.append("STORE 2")
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + expression.value2.name, self.symbols.get_array_beginning(prefix + expression.value2.name))}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + expression.value2.position)}")
                    inner_code.append("STORE 1")
                    inner_code.append("LOADI 1")
                    inner_code.append("ADD 2")
                    
                    linenum += 6
            else:
                if self.symbols.is_declared(expression.value2):
                    inner_code.append(f"ADD  {self.symbols.get_const(expression.value2)}")
                    linenum += 1
                else:
                    #? put down previously loaded value
                    #* this is inefficient but will get optimized in pre- and postprocessing
                    inner_code.append("STORE 1")
                    linenum += 1
                    
                    self.symbols.add_const(expression.value2)
                    inner_code.append(f"SET {expression.value2}")
                    inner_code.append(f"STORE {self.symbols.get_const(expression.value2)}")
                    linenum += 2
                    
                    # load the previously set aside value
                    inner_code.append("LOAD 1")
                    inner_code.append(f"ADD {self.symbols.get_const(expression.value2)}")
                    linenum += 2
                    
            
            
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
                inner_code.append(f"LOAD  {self.symbols.get_variable(prefix + expression.value1.name)}")
                linenum += 1
            elif isinstance(expression.value1, nd.ArrayPosition):
                if isinstance(expression.value1.position, int):
                    inner_code.append(f"LOAD {self.symbols.get_array_position(prefix + expression.value1.name, expression.value1.position)}")
                    linenum += 1
                else:
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + expression.value1.name, self.symbols.get_array_beginning(prefix + expression.value1.name))}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + expression.value1.position)}")
                    inner_code.append("STORE 1")
                    inner_code.append(f"LOADI 1")
                    
                    linenum += 4
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
                inner_code.append(f"SUB  {self.symbols.get_variable(prefix + expression.value2.name)}")
                linenum += 1
            elif isinstance(expression.value2, nd.ArrayPosition):
                if isinstance(expression.value2.position, int):
                    inner_code.append(f"SUB {self.symbols.get_array_position(prefix + expression.value2.name, expression.value2.position)}")
                    linenum += 1
                    
                else:
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + expression.value2.name, self.symbols.get_array_beginning(prefix + expression.value2.name))}")
                    inner_code.append(f"SUB {self.symbols.get_variable(prefix + expression.value2.position)}")
                    inner_code.append("STORE 1")
                    inner_code.append("LOADI 1")
                    
                    linenum += 4
            else:
                if self.symbols.is_declared(expression.value2):
                    inner_code.append(f"SUB  {self.symbols.get_const(expression.value2)}")
                    linenum += 1
                else:
                    #? put down previously loaded value
                    #* this is inefficient but will get optimized in pre- and postprocessing
                    inner_code.append("STORE 1")
                    linenum += 1
                    
                    self.symbols.add_const(expression.value2)
                    inner_code.append(f"SET {expression.value2}")
                    inner_code.append(f"STORE {self.symbols.get_const(expression.value2)}")
                    linenum += 2
                    
                    # load the previously set aside value
                    inner_code.append("LOAD 1")
                    inner_code.append(f"SUB {self.symbols.get_const(expression.value2)}")
                    linenum += 3
            
            # inner_code.append("STORE 1")
            # linenum += 1
            
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
        
        #? subtract the two values
        if isinstance(condition.value1, nd.Identifier):
            inner_code.append(f"LOAD {self.symbols.get_variable(prefix + condition.value1.name)}")
            linenum += 1
        elif isinstance(condition.value1, nd.ArrayPosition):
                if isinstance(condition.value1.position, int):
                    inner_code.append(f"LOAD {self.symbols.get_array_position(prefix + condition.value1.name, condition.value1.position)}")
                    
                else:
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + condition.value1.name, self.symbols.get_array_beginning(prefix + condition.value1.name))}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + condition.value1.position)}")
                    inner_code.append("STORE 1")
                    inner_code.append(f"LOADI 1")
                    
                    linenum += 4
        else:
            if self.symbols.is_declared(condition.value1):
                inner_code.append(f"LOAD {self.symbols.get_const(condition.value1)}")
                linenum += 1
            else:
                self.symbols.add_const(condition.value1)
                inner_code.append(f"SET {condition.value1}")
                inner_code.append(f"STORE {self.symbols.get_const(condition.value1)}")
                linenum += 2
                
        if isinstance(condition.value2, nd.Identifier):
            inner_code.append(f"SUB {self.symbols.get_variable(prefix + condition.value2.name)}")
            linenum += 1
        elif isinstance(condition.value2, nd.ArrayPosition):
                if isinstance(condition.value2.position, int):
                    inner_code.append(f"SUB {self.symbols.get_array_position(prefix + condition.value2.name, condition.value2.position)}")
                    linenum += 1
                else:
                    inner_code.append(f"SET {self.symbols.get_array_position(prefix + condition.value2.name, self.symbols.get_array_beginning(prefix + condition.value2.name))}")
                    inner_code.append(f"ADD {self.symbols.get_variable(prefix + condition.value2.position)}")
                    inner_code.append("STORE 1")
                    inner_code.append(f"LOADI 1")
                    
                    linenum += 4
        else:
            if self.symbols.is_declared(condition.value2):
                inner_code.append(f"SUB {self.symbols.get_const(condition.value2)}")
                linenum += 1
            else:
                # put down the restult of previous LOAD because the accumulator is needed for SET
                #? this does not warrant a TODO because it will get optimized when I make a preprocessor initializing all constants in advance
                inner_code.append(f"STORE 1")
                self.symbols.add_const(condition.value2)
                inner_code.append(f"SET {condition.value2}")
                inner_code.append(f"STORE {self.symbols.get_const(condition.value2)}")
                # load back what we put down in 1
                inner_code.append(f"LOAD 1")
                inner_code.append(f"SUB {self.symbols.get_const(condition.value2)}")
                linenum += 5
        
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
            
        