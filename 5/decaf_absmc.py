import random

class AbstractMI:
    def __init__(self):
        self.static_offset_counter = 0
        self.instance_offset_counter = 0
        self.argument_counter = 1
        self.preserved = dict() #{class_name: {static, instance, offset}}
        self.offset = dict() #{field_id: offset}
        self.variables = dict() #{variable_id: register}
        self.register_counter = 0

    def restore_info(self, name):
        self.instance_offset_counter = self.preserved[name]['instance_offset_counter']

    def reset_arguments(self):
        self.argument_counter = 1

    def reset(self, name):
        self.preserved[name] = dict()
        self.preserved[name]['instance_offset_counter'] = self.instance_offset_counter
        self.instance_offset_counter = 0
        self.variables = dict()

    def static_directive(self):
        return f".static_data {self.static_offset_counter}\n"
    
    def assign_label(self, prefix="L_", postfix=""):
        random_number = random.randint(0,9999)
        return f"{prefix}{random_number}{postfix}"

    def assign_register(self, type='temp'):
        if type == 'temp':
            register_type = "t"
            dst = self.register_counter
            self.register_counter+=1
        else:
            register_type = "a"
            dst = self.argument_counter
            self.argument_counter+=1
        
        return register_type + str(dst)

    def set_offset(self, id, applicability):
        if applicability == 'static':
            self.offset[id] = self.static_offset_counter
            self.static_offset_counter+=1
        else:
            self.offset[id] = self.instance_offset_counter
            self.instance_offset_counter+=1

    def get_offset(self, id):
        return self.offset[id]

    def bind_variable(self, id, kind = 'local'):
        if self.variables.get(id, None) == None:
            if kind == 'local':
                self.variables[id] = self.assign_register()
            else:
                self.variables[id] = self.assign_register('argument')

        return self.variables[id]

    def move_constant(self, r, i, type):
        return f"move_immed_f {r}, {float(i)}\n" if type == 'float' else f"move_immed_i {r}, {i}\n"

    def move(self, r1, r2):
        return f"move {r1}, {r2}\n"

    def add(self, r1, r2, r3, type):
        return f"fadd {r1}, {r2}, {r3}\n" if type == 'float' else f"iadd {r1}, {r2}, {r3}\n"
    
    def sub(self, r1, r2, r3, type):
        return f"fsub {r1}, {r2}, {r3}\n" if type == 'float' else f"isub {r1}, {r2}, {r3}\n"
    
    def mul(self, r1, r2, r3, type):
        return f"fmul {r1}, {r2}, {r3}\n" if type == 'float' else f"imul {r1}, {r2}, {r3}\n"
    
    def div(self, r1, r2, r3, type):
        return f"fdiv {r1}, {r2}, {r3}\n" if type == 'float' else f"idiv {r1}, {r2}, {r3}\n"
    
    def mod(self, r1, r2, r3, type):
        return f"fmod {r1}, {r2}, {r3}\n" if type == 'float' else f"imod {r1}, {r2}, {r3}\n"
    
    def gt(self, r1, r2, r3, type):
        return f"fgt {r1}, {r2}, {r3}\n" if type == 'float' else f"igt {r1}, {r2}, {r3}\n"
    
    def geq(self, r1, r2, r3, type):
        return f"fgeq {r1}, {r2}, {r3}\n" if type == 'float' else f"igeq {r1}, {r2}, {r3}\n"
    
    def lt(self, r1, r2, r3, type):
        return f"flt {r1}, {r2}, {r3}\n" if type == 'float' else f"ilt {r1}, {r2}, {r3}\n"
    
    def leq(self, r1, r2, r3, type):
        return f"fleq {r1}, {r2}, {r3}\n" if type == 'float' else f"ileq {r1}, {r2}, {r3}\n"

    #type2 must be converted to type1
    def convert(self,r1, r2, desired_type):
        if desired_type == 'float':
            return f"itof {r1}, {r2}\n"
        else:
            return f"ftoi {r1}, {r2}\n"

    def label(self, label):
        return f"{label}:\n"

    def branch(self, r1, L, condition):
        if condition == None:
            return f"jmp {L}\n"
        elif condition == True:
            return f"bnz {r1}, {L}\n"
        else:
            return f"bz {r1}, {L}\n"

    def hload(self, r1, r2, r3):
        return f"hload {r1}, {r2}, {r3}\n"

    def hstore(self, r1, r2, r3):
        return f"hstore {r1}, {r2}, {r3}\n"

    def halloc(self, r1, r2):
        return f"halloc {r1}, {r2}\n"

    def call(self, L):
        return f"call {L}\n"

    def ret(self):
        return "ret\n"

    def save(self, r):
        return f"save {r}\n"

    def save_arguments(self, size):
        code = ""
        for i in range(size+1):
            code += self.save(f"a{i}")
        return code

    def restore(self, r):
        return f"restore {r}\n"
    
    def restore_arguments(self, size):
        code = ""
        for i in reversed(range(size+1)):
            code += self.restore(f"a{i}")
        return code
    
    #Get the number of non-static fields of the class
    def get_class_size(self, name):
        offset_record = self.preserved.get(name, None)
        if offset_record:
            return offset_record['instance_offset_counter']
        else:
            return self.instance_offset_counter