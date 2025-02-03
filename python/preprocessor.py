from symbol_table import SymbolTable
import nodes as nd

class Preprocessor:
    def __init__(self):
        
        self.consts = set()
        self.procedures = set()
        
        
    def preprocess(self, tree : nd.Program):
        for procedure in tree.procedures.procedures:
            self.search_commands(procedure.commands)
        
        self.search_commands(tree.main.commands)
        
        return self.consts, self.procedures
        
    def search_commands(self, commands : nd.Commands):
        for comm in commands.commands:
            if isinstance(comm, nd.Assign):
                expr = comm.assignment
                if expr.operator == "MUL":
                    if expr.value1 not in [0, 1, 2, -1]:
                        if expr.value2 not in [0, 1, 2, -1]:
                            # prefixed with 0 so that it definitely cannot share a name with a real procedure
                            self.procedures.add("0_MUL")
                    
                    self.consts.add(0)
                    self.consts.add(1)
                    
                if expr.operator == "DIV":
                    if expr.value2 not in [0, 1, 2] and expr.value2 != 0:
                        self.procedures.add("0_DIV")
                    
                    self.consts.add(0)
                    self.consts.add(1)
                    
                if expr.operator == "MOD":
                    if expr.value2 not in [0, 1, 2] and expr.value2 != 0:
                        self.procedures.add("0_MOD")
                    
                    
                    self.consts.add(0)
                    self.consts.add(1)
                    
                if isinstance(expr.value1, int):
                    self.consts.add(expr.value1)
                
                if isinstance(expr.value2, int):
                    self.consts.add(expr.value2)
            
            elif isinstance(comm, nd.IfStatement):

                self.search_condition(comm.condition)
                    
                self.search_commands(comm.commands)
                
                if comm.else_commands is not None:
                    self.search_commands(comm.else_commands)
                
            if isinstance(comm, nd.WhileLoop):
                
                self.search_condition(comm.condition)
                self.search_commands(comm.commands)
                
            if isinstance(comm, nd.RepeatUntil):
                self.search_condition(comm.condition)
                self.search_commands(comm.commands)
                
            if isinstance(comm, nd.ForTo) or isinstance(comm, nd.ForDownto):
                self.consts.add(1)
                
                if isinstance(comm.start_value, int):
                    self.consts.add(comm.start_value)
                if isinstance(comm.end_value, int):
                    self.consts.add(comm.end_value)
                    
                self.search_commands(comm.commands)
                
            if isinstance(comm, nd.ProcCall):
                self.procedures.add(comm.pid)
                
                # arguments specifically cannot be numbered
                
            if isinstance(comm, nd.Read):
                # reading does not use any integers
                
                pass
            
            if isinstance(comm, nd.Write):
                if isinstance(comm.value, int):
                    self.consts.add(comm.value)
                
                
            
    def search_condition(self, cond : nd.Condition):
        if isinstance(cond.value1, int):
            self.consts.add(cond.value1)
            
        if isinstance(cond.value2, int):
            self.consts.add(cond.value2)
                    
                