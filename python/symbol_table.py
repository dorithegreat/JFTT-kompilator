from contextlib import suppress

class Array:
    def __init__(self, name, first_index, last_index, memory_location):
        self.name = name
        self.first_index = first_index
        self.last_index = last_index
        self.memory_location = memory_location
        
    def get_at(self, index):
        # if self.first_index <= index <= self.last_index:
        #     return self.memory_location + index - self.first_index
        # else:
        #     raise Exception("Index ", index, " not in array ", self.name, ". Array indexed from ", self.first_index, " to ", self.last_index)
        return self.memory_location + index - self.first_index

class Variable:
    def __init__(self, name, memory_location, initialized : bool):
        self.name = name
        self.memory_location = memory_location
        self.initialized = initialized
        
class Constant:
    def __init__(self, value, memory_location):
        self.value = value
        self.memory_location = memory_location
        
class Iterator:
    def __init__(self, name, memory_location, condition_location):
        self.name = name
        self.memory_location = memory_location
        self.condition_location = condition_location
        
class Reference:
    def __init__(self, name, memory_location):
        self.name = name
        self.memory_location = memory_location
        
class Procedure:
    def __init__(self, name, linenum, return_spot):
        self.args = []
        self.name = name
        self.linenum = linenum
        # fun fact: you can't name a variable "return"
        self.return_spot = return_spot
        
        
class ArrayReference:
    def __init__(self, name, memory_location):
        self.name = name
        self.memory_location = memory_location
    
        

class SymbolTable(dict):
    
    
    
    # memory is virtually infinite so I will not be caring about optimizing its use
    first_available_memory = 10
    
    consts = {}
    procedures = {}
    
    def __init__(self):
        super().__init__()
        
    def add_variable(self, name):
        if name in self:
            raise Exception(f"Redeclaration of variable {name}")
        
        self.setdefault(name, Variable(name, self.first_available_memory, False))
        self.first_available_memory += 1
        
        
    def add_array(self, name, first_index, last_index):
        if name in self:
            raise Exception("Redeclaration of variable ", name)
        
        if first_index > last_index:
            raise Exception("Improper declaration of array ", name, ", first index larger thatn last index")
        
        self.setdefault(name, Array(name, first_index, last_index, self.first_available_memory))
        self.first_available_memory += last_index - first_index + 1
        
    def add_const(self, value):
        if value in self.consts:
            # it's not illegal to try to add the same constant twice
            # but it should not be allocated again
            return
        
        self.consts.setdefault(value, Constant(value, self.first_available_memory))
        self.first_available_memory += 1
        
    def add_iterator(self, name):
        if name in self:
            raise Exception("Trying to use a for loop iterator with the same name as declared variable")
        
        self.setdefault(name, Iterator(name, self.first_available_memory, self.first_available_memory + 1))
        self.first_available_memory += 2
        
    
    def get_variable(self, var):
        if var in self:
            return self.get(var).memory_location
        else:
            raise Exception("Referring to an unallocated variable: ", var)
        
    def get_const(self, const):
        if const in self.consts:
            return self.consts.get(const).memory_location
        # else:
        #     # if it's not already in the list of consts just allocate it
        #     self.add_const(const)
        #     return self.get(const).memory_location
        
    def get_array_position(self, arr, pos):
        if arr in self:
            if not isinstance(self.get(arr), Array):
                raise Exception(f"Trying to access an index of a variable {arr} which is not an array")
            
            return self.get(arr).get_at(pos)
        
    def get_array_beginning(self, arr):
        if arr in self:
            return self.get(arr).first_index
        
    def get_iterator(self, name):
        if name in self:
            return self.get(name).memory_location
        else:
            # I honestly can't see how this would ever occur but why not put it here
            raise Exception("Referring to an undeclared iterator")
        
    def is_declared(self, const):
        if const in self.consts:
            return True
        else:
            return False
        
    # it's perfectly legal to have two non-nested loops using iterators with the same name
    def dealocate_iterator(self, name):
        if name in self:
            self.pop(name)
            
    def get_iterator_condition(self, iterator):
        if iterator in self:
            return self.get(iterator).condition_location
        
    def add_procedure(self, name, place):
        if name in self.procedures:
            raise Exception("Two procedures defined with the same name " + name)
        else:
            self.procedures.setdefault(name, Procedure(name, place, self.first_available_memory))
            self.first_available_memory += 1
            
    def add_proc_arg(self, proc, name):
        if proc in self.procedures:
            self.procedures.get(proc).args.append(self.get(name))
            
    def get_proc_arg(self, proc):
        if proc in self.procedures:
            return self.procedures.get(proc).args
        else:
            raise Exception(f"Referring to an undefined procedure {proc}")
        
        
    def add_reference(self, name):
        #can this even occur?
        if name in self:
            raise Exception(f"Reference with the same name as an already existing variable ({name})")
        else:
            self.setdefault(name, Reference(name, self.first_available_memory))
            self.first_available_memory += 1

    def add_array_reference(self, name):
        if name in self:
            raise Exception(f"Array reference with the same name as already existing variable ({name})")
        else:
            self.setdefault(name, ArrayReference(name, self.first_available_memory))
            self.first_available_memory += 1
            
    def is_reference(self, name):
        if name not in self:
            raise Exception(f"Referring to an unalocated variable: {name}")
        var = self.get(name)
        if isinstance(var, Reference):
            return True
        # extend to arrays too?
        else:
            return False
        
    def is_iterator(self, name):
        if name not in self:
            raise Exception(f"Referring to an unalocated variable: {name}")
        var = self.get(name)
        if isinstance(var, Iterator):
            return True
        else:
            return False
        
    def get_proc_position(self, name):
        if name in self.procedures:
            return self.procedures.get(name).linenum
        
    def get_return(self, proc):
        if proc in self.procedures:
            return self.procedures.get(proc).return_spot
        
    def is_array_reference(self, name):
        if name not in self:
            raise Exception(f"Referring to an unalocated array {name}")
        var = self.get(name)
        if isinstance(var, ArrayReference):
            return True
        else:
            return False
        
        
    def is_array(self, name):
        if name in self:
            if isinstance(self.get(name), Array):
                return True
            else:
                return False

    def is_initialized(self, name):
        if name in self:
            if isinstance(self.get(name), Variable):
                return self.get(name).initialized
            else:
                return True
    
    def mark_as_initialized(self,name):
        if name in self and isinstance(self.get(name), Variable):
            self.get(name).initialized = True
        else:
            raise Exception(f"no variable with such name: {name}")
        
if __name__ == "__main__":
    s = SymbolTable()
    s.add_variable("a")
    s.mark_as_initialized("a")
    print(s.is_initialized("a"))