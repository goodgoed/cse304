class AbstractMI:
    def __init__(self):
        self.static_offset_counter = 0
        self.instance_offset_counter = 0
        self.offset = dict() #for fields
        self.base_address = dict()
        self.variables = None #{name: register (ex. t0)}
        self.register_counter = 0

    def assign_register(self):
        dst = self.register_counter
        self.register_counter+=1
        return "t" + str(dst)

    def move_constant(self, r, i, type):
        return f"move_immed_i {r}, {i}" if type == 'int' else f"move_immed_f {r}, {i}"

    def move(self, r1, r2):
        return f"move {r1}, {r2}"

    def add(self, r1, r2, r3, type):
        return f"iadd {r1}, {r2}, {r3}" if type == 'int' else f"fadd {r1}, {r2}, {r3}"
    
    def sub(self, r1, r2, r3, type):
        return f"isub {r1}, {r2}, {r3}" if type == 'int' else f"fsub {r1}, {r2}, {r3}"
    
    def mul(self, r1, r2, r3, type):
        return f"imul {r1}, {r2}, {r3}" if type == 'int' else f"fmul {r1}, {r2}, {r3}"
    
    def div(self, r1, r2, r3, type):
        return f"idiv {r1}, {r2}, {r3}" if type == 'int' else f"fdiv {r1}, {r2}, {r3}"
    
    def mod(self, r1, r2, r3, type):
        return f"imod {r1}, {r2}, {r3}" if type == 'int' else f"fmod {r1}, {r2}, {r3}"
    
    def gt(self, r1, r2, r3, type):
        return f"igt {r1}, {r2}, {r3}" if type == 'int' else f"fgt {r1}, {r2}, {r3}"
    
    def geq(self, r1, r2, r3, type):
        return f"igeq {r1}, {r2}, {r3}" if type == 'int' else f"fgeq {r1}, {r2}, {r3}"
    
    def lt(self, r1, r2, r3, type):
        return f"ilt {r1}, {r2}, {r3}" if type == 'int' else f"flt {r1}, {r2}, {r3}"
    
    def leq(self, r1, r2, r3, type):
        return f"ileq {r1}, {r2}, {r3}" if type == 'int' else f"fleq {r1}, {r2}, {r3}"

    #type2 must be converted to type1
    def convert(self, type1, type2, r1, r2):
        if type1 == type2:
            return ""
        elif type2 == 'float':
            return f"ftoi {r1}, {r2}"
        else:
            return f"itof {r1}, {r2}"

    def branch(self, r1, L, condition):
        if condition == None:
            return f"jmp {L}"
        elif condition == True:
            return f"bnz {r1}, {L}"
        else:
            return f"bz {r1}, {L}"

    def hload(self, r1, r2, r3):
        return f"hload {r1}, {r2}, {r3}"

    def hstore(self, r1, r2, r3):
        return f"hstore {r1}, {r2}, {r3}"

    def halloc(self, r1, r2):
        return f"halloc {r1}, {r2}"

    def call(self, L):
        return f"call {L}"

    def ret(self):
        return "ret"

    def save(self, r):
        return f"save {r}"

    def restore(self, r):
        return f"restore {r}"
