from symbol_table import SymbolTable
import nodes as nd

class CodeGenerator:
    def __init__(self, tree):
        self.tree : nd.Program = tree
        self.symbols = SymbolTable()
        
    
    def generate(self):
        self.generate_procedures(self.tree.procedures)
        self.generate_main(self.tree.main)
    
    
    def generate_procedures(self, procedures : nd.Procedures):
        pass
    
    #? distinct from generate_procedures()
    # that one is plural, this one is singular
    def generate_procedure(self, procedure : nd.Procedure):
        pass
    
    def generate_main(self, main : nd.Main):
        pass
    
    def generate_commands(self, commands : nd.Commands):
        pass
    
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
        