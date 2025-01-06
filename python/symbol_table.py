class Array:
    def __init__(self, name, first_index, last_index, memory_location):
        self.name = name
        self.first_index = first_index
        self.last_index = last_index
        self.memory_location = memory_location
        
    def get_at(self, index):
        if self.first_index <= index <= self.last_index:
            return self.memory_location + index - self.first_index
        else:
            raise Exception("Index ", index, " not in array ", self.name, ". Array indexed from ", self.first_index, " to ", self.last_index)
        

class Variable:
    def __init__(self, name, memory_location):
        self.name = name
        self.memory_location = memory_location

class SymbolTable(dict):
    
    # arbitrarily set at 10 for now
    # TODO should probably be set at maximum number of arguments of any procedure + 1
    # but not less than x
    
    
    # memory is virtually infinite so I will not be caring about optimizing its use
    first_available_memory = 10
    
    def __init__(self):
        super().__init__()
        
    def add_variable(self, name):
        if name in self:
            raise Exception("Redeclaration of variable ", name)
        
        self.setdefault(name, Variable(name, self.first_available_memory))
        self.first_available_memory += 1
        
        
    def add_array(self, name, first_index, last_index):
        if name in self:
            raise Exception("Redeclaration of variable ", name)
        
        if first_index > last_index:
            raise Exception("Improper declaration of array ", name, ", first index larger thatn last index")
        
        self.setdefault(name, Array(name, first_index, last_index, self.first_available_memory))
        self.first_available_memory += last_index - first_index + 1
        
    def add_const(self, value):
        pass
    
    def get_variable(self, var):
        if var in self:
            return self.get(var).memory_location
        else:
            raise Exception("Referring to an unallocated variable: ", var)
        