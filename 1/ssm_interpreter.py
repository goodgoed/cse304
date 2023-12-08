# name: Seungwon An
# netid: seunan
# student ID number: 115236174

import sys
import os
import re

def error(msg):
    print(f'ERROR: {msg}', file=sys.stderr)
    exit()

class Token:
    def __init__(self,lexem, type):
        self.lexem = lexem
        self.type = type
    def __repr__(self):
        return f'({self.lexem}:{self.type})'
    def getToken(self):
        return (self.lexem, self.type)

class Lexer:
    def __init__(self, text, rules):
        self.text = re.sub(r'#.*\n*', "", text)
        self.rules = []
        for rule, type in rules:
            rule_with_group = f'(?P<{type}>{rule})'
            self.rules.append(rule_with_group)
        self.rules = re.compile("|".join(self.rules))
    
    def scan(self):
        tokens = []
        index = 0
        whitespace_required = False
        while index < len(self.text):
            is_whitespace = re.match(r'\s+', self.text[index]) != None

            if not is_whitespace and whitespace_required:
                error("INSTRUCTION AND ARGUMENT SHOULD BE SEPARATED BY SPACE!")

            if is_whitespace:
                index+=1
                if whitespace_required:
                    whitespace_required = False
                continue

            match = self.rules.match(self.text, index)
            if match:
                type = match.lastgroup
                lexem = re.sub(r'\s+', "", match.group(0))
                if type == 'LABEL_INDICATOR':
                    lexem = lexem[:len(lexem)-1]
                token = Token(lexem ,type)
                tokens.append(token)

                index=match.end()
                whitespace_required = True
            else:
                tokens.append(Token("invalid", "INVALID"))
        return tokens

class Parser:
    def __init__(self, tokens, table):
        self.tokens = tokens
        self.table = table
    def parse(self):
        index = 0
        parsed_tokens = []
        labels = dict()
        label_matcher = []
        expected_type = ("LABEL_INDICATOR", "PUSH_OPERATOR", "SIMPLE_INSTRUCTION", "LABEL_INSTRUCTION")

        while index < len(self.tokens):
            current_token = self.tokens[index]
            lexem, type = current_token.getToken()
            type = self.table[type] if type not in ("LABEL_INDICATOR", "LABEL_IDENTIFIER", "INTEGER") else type

            if type == "INVALID":
                error('NO SPECIAL CHARACTERS OR UPPER CASED LETTERS ARE ALLOWED!')
            if type not in expected_type:
                expected_string = ", ".join(expected_type)
                error(f"Expected {expected_string}")

            parsed_tokens.append(current_token)
            if type == "PUSH_OPERATOR":
                expected_type = ("INTEGER", "")
            elif type == "INTEGER":
                expected_type = ("LABEL_INDICATOR", "PUSH_OPERATOR", "SIMPLE_INSTRUCTION", "LABEL_INSTRUCTION")
            elif type == "SIMPLE_INSTRUCTION":
                expected_type = ("LABEL_INDICATOR", "PUSH_OPERATOR", "SIMPLE_INSTRUCTION", "LABEL_INSTRUCTION")
            elif type == "LABEL_INSTRUCTION":
                expected_type = ("LABEL_IDENTIFIER")
            elif type == 'LABEL_INDICATOR':
                expected_type = ("LABEL_INDICATOR", "PUSH_OPERATOR", "SIMPLE_INSTRUCTION", "LABEL_INSTRUCTION")
                labels[lexem] = index
            elif type == 'LABEL_IDENTIFIER':
                expected_type = ("LABEL_INDICATOR", "PUSH_OPERATOR", "SIMPLE_INSTRUCTION", "LABEL_INSTRUCTION")
                label_matcher.append(lexem)

            index+=1
        
        for label in label_matcher:
            if label not in labels.keys():
                error("LABEL DOES NOT MATCH!")
        
        return (parsed_tokens, labels)

class Interpreter:
    def __init__(self, tokens, labels, stack, store):
        self.tokens = tokens
        self.labels = labels
        self.stack = stack
        self.store = store
    def run(self):
        index = 0

        while index < len(self.tokens):
            lexem, type = self.tokens[index].getToken()

            if type == "ILDC":
                self.stack.push(self.tokens[index+1].lexem)
                index+=1
            elif type in ('IADD', 'ISUB', 'IMUL', 'IDIV','IMOD'):
                table = {
                    'IADD': lambda x,y: x+y,
                    'ISUB': lambda x,y: y-x,
                    'IMUL': lambda x,y: x*y,
                    'IDIV': lambda x,y: y/x,
                    'IMOD': lambda x,y: y%x,
                }
                num_1 = int(self.stack.pop())
                num_2 = int(self.stack.pop())
                self.stack.push(table[type](num_1,num_2))
            elif type == 'POP':
                self.stack.pop()
            elif type == 'DUP':
                num = self.stack.top()
                self.stack.push(num)
            elif type == 'SWAP':
                first = self.stack.pop()
                second = self.stack.pop()
                self.stack.push(first)
                self.stack.push(second)
            elif type == 'LOAD':
                num = int(self.stack.pop())
                if num in self.store:
                    self.stack.push(self.store[num])
                else:
                    error(f"THERE IS NO ELEMENT IN STORE AT ADDRESS {address}")
            elif type == 'STORE':
                num = int(self.stack.pop())
                address = int(self.stack.pop())
                self.store[address] = num
            elif type == 'JZ':
                num = self.stack.pop()
                if num == 0:
                    lexem = self.tokens[index + 1].lexem
                    index = labels[lexem] - 1
            elif type == 'JNZ':
                num = self.stack.pop()
                if num != 0:
                    lexem = self.tokens[index + 1].lexem
                    index = labels[lexem] - 1
            elif type == 'JMP':
                lexem = self.tokens[index + 1].lexem
                index = labels[lexem] - 1
            else:
                pass

            index+=1

        if not self.stack.empty():
            print(self.stack.top())
        else:
            print(None)

class Stack:
    def __init__(self):
        self.stack = []
    # FOR DEBUGGING
    def __repr__(self):
        text = ""
        for num in self.stack:
            text = f'{num}, {text}'
        return text
    def size(self):
        return len(self.stack)
    def empty(self):
        return self.size() == 0
    def top(self):
        if self.empty():
            error("NO ELEMENTS IN THE STACK")
        last_index = len(self.stack) - 1
        return self.stack[last_index]
    def push(self, number):
        self.stack.append(number)
    def pop(self):
        if self.empty():
            error("NO ELEMENTS IN THE STACK")
        return self.stack.pop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Need to provide file path as an argument!")
        exit()

    filePath = sys.argv[1]
    if not os.path.exists(filePath):
        print("The file does not exist!")
        exit()

    file = open(filePath, 'r')
    text = file.read()
    file.close()

    rules = [
        (r'i\s*l\s*d\s*c', 'ILDC'),
        (r'i\s*a\s*d\s*d', 'IADD'),
        (r'i\s*s\s*u\s*b', 'ISUB'),
        (r'i\s*m\s*u\s*l', 'IMUL'),
        (r'i\s*d\s*i\s*v', 'IDIV'),
        (r'i\s*m\s*o\s*d', 'IMOD'),
        (r'p\s*o\s*p', 'POP'),
        (r'd\s*u\s*p', 'DUP'),
        (r's\s*w\s*a\s*p', 'SWAP'),
        (r'j\s*z', 'JZ'),
        (r'j\s*n\s*z', 'JNZ'),
        (r'j\s*m\s*p', 'JMP'),
        (r's\s*t\s*o\s*r\s*e', 'STORE'),
        (r'l\s*o\s*a\s*d', 'LOAD'),
        (r'[a-z][\w\d]*:', 'LABEL_INDICATOR'),
        (r'[a-z][\w\d]*', 'LABEL_IDENTIFIER'),
        (r'(-)?(0|[1-9][0-9]*)', 'INTEGER'),
    ]
    table = {
        "ILDC": "PUSH_OPERATOR",
        "IADD": "SIMPLE_INSTRUCTION",
        "ISUB": "SIMPLE_INSTRUCTION",
        "IMUL": "SIMPLE_INSTRUCTION",
        "IDIV": "SIMPLE_INSTRUCTION",
        "IMOD": "SIMPLE_INSTRUCTION",
        "POP": "SIMPLE_INSTRUCTION",
        "DUP": "SIMPLE_INSTRUCTION",
        "SWAP": "SIMPLE_INSTRUCTION",
        "JZ": "LABEL_INSTRUCTION",
        "JNZ": "LABEL_INSTRUCTION",
        "JMP": "LABEL_INSTRUCTION",
        "STORE": "SIMPLE_INSTRUCTION",
        "LOAD": "SIMPLE_INSTRUCTION",
    }

    lexer = Lexer(text, rules)
    tokens = lexer.scan()
    parsed_tokens, labels = Parser(tokens, table).parse()

    my_stack = Stack()
    my_store = dict()
    interpreter = Interpreter(parsed_tokens,labels,my_stack,my_store)
    interpreter.run()
