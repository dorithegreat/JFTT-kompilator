from symbol_table import SymbolTable


class Postprocessor:
    def __init__(self, symbols : SymbolTable):
        self.symbols = symbols
    
    def postprocess(self, code):
        self.resolve_jumps(code)
    
    def resolve_jumps(self, code):
        for line in code:
            if line == "HALT":
                return
            
            command, argument = line.split()
            
            if command == "JUMP" and not self.isnumber(argument):
                code[code.index(line)] = f"JUMP {self.symbols.get_proc_position(argument) - code.index(line)}"
                
            if command == "SET" and not self.isnumber(argument):
                code[code.index(line)] = f"SET {code.index(line) + 3}"
                
    def isnumber(self, str):
        try:
            int(str)
            return True
        except Exception:
            return False