import ply.lex as lex
import ply.yacc as yacc
import tkinter as tk
from tkinter import messagebox
import re 

# Define tokens
tokens = [
    ("IF", r'\bif\b'),
    ("ELSE", r'\belse\b'),
    ("NUMBER", r'\d+'),
    ("IDENTIFIER", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("PLUS", r'\+'),
    ("MINUS", r'-'),
    ("MULTIPLY", r'\*'),
    ("DIVIDE", r'/'),
    ("EQUALS", r'='),
    ("LPAREN", r'\('),
    ("RPAREN", r'\)'),
    ("LBRACE", r'\{'),
    ("RBRACE", r'\}'),
    ("SEMICOLON", r';'),
    ("COMPARISON", r'==|!=|<=|>=|<|>'),
    ("WHITESPACE", r'\s+'),  # Ignore spaces
]

# Lexer for manual tokenization
def lexer(source_code):
    token_list = []
    while source_code:
        match = None
        for token_type, regex in tokens:
            regex_match = re.match(regex, source_code)
            if regex_match:
                match = regex_match
                lexeme = match.group(0)
                if token_type != "WHITESPACE":
                    token_list.append((token_type, lexeme))
                source_code = source_code[len(lexeme):]
                break
        if not match:
            raise ValueError(f"Unexpected character: {source_code[0]}")
    return token_list

# Lexer using PLY


class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

# Parser for manual interpretation
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def consume(self, token_type):
        if self.current_token() and self.current_token()[0] == token_type:
            self.position += 1
        else:
            raise ValueError(f"Expected {token_type}, got {self.current_token()}")

    def parse_expression(self):
        node = self.parse_term()
        while self.current_token() and self.current_token()[0] in ("PLUS", "MINUS"):
            op = self.current_token()
            self.consume(op[0])
            right = self.parse_term()
            node = ASTNode("binary_op", op[1], [node, right])
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token() and self.current_token()[0] in ("MULTIPLY", "DIVIDE"):
            op = self.current_token()
            self.consume(op[0])
            right = self.parse_factor()
            node = ASTNode("binary_op", op[1], [node, right])
        return node

    def parse_factor(self):
        if self.current_token()[0] == "NUMBER":
            token = self.current_token()
            self.consume("NUMBER")
            return ASTNode("number", token[1])
        elif self.current_token()[0] == "IDENTIFIER":
            token = self.current_token()
            self.consume("IDENTIFIER")
            return ASTNode("identifier", token[1])
        elif self.current_token()[0] == "LPAREN":
            self.consume("LPAREN")
            node = self.parse_expression()
            self.consume("RPAREN")
            return node
        else:
            raise ValueError(f"Unexpected token: {self.current_token()}")

    def parse_comparison(self):
        left = self.parse_expression()
        if self.current_token() and self.current_token()[0] == "COMPARISON":
            op = self.current_token()
            self.consume("COMPARISON")
            right = self.parse_expression()
            return ASTNode("comparison", op[1], [left, right])
        return left

    def parse_statement(self):
        if self.current_token()[0] == "IF":
            self.consume("IF")
            self.consume("LPAREN")
            condition = self.parse_comparison()
            self.consume("RPAREN")
            self.consume("LBRACE")
            if_body = self.parse_block()
            self.consume("RBRACE")
            else_body = None
            if self.current_token() and self.current_token()[0] == "ELSE":
                self.consume("ELSE")
                self.consume("LBRACE")
                else_body = self.parse_block()
                self.consume("RBRACE")
            return ASTNode("if_else", None, [condition, if_body, else_body])
        elif self.current_token()[0] == "IDENTIFIER":
            identifier = self.current_token()
            self.consume("IDENTIFIER")
            self.consume("EQUALS")
            value = self.parse_expression()
            self.consume("SEMICOLON")
            return ASTNode("assignment", identifier[1], [value])
        else:
            raise ValueError(f"Unexpected token in statement: {self.current_token()}")

    def parse_block(self):
        statements = []
        while self.current_token() and self.current_token()[0] not in ("RBRACE", None):
            statements.append(self.parse_statement())
        return ASTNode("block", None, statements)

    def parse(self):
        return self.parse_block()
    




                
# Interpreter and Compiler code here...
class Interpreter:
    def __init__(self):
        self.variables = {}

    def interpret(self, node):
        if node.node_type == "number":
            return int(node.value)
        elif node.node_type == "identifier":
            if node.value in self.variables:
                return self.variables[node.value]
            else:
                raise ValueError(f"Undefined variable: {node.value}")
        elif node.node_type == "binary_op":
            left = self.interpret(node.children[0])
            right = self.interpret(node.children[1])
            if node.value == "+":
                return left + right
            elif node.value == "-":
                return left - right
            elif node.value == "*":
                return left * right
            elif node.value == "/":
                return left // right
        elif node.node_type == "comparison":
            left = self.interpret(node.children[0])
            right = self.interpret(node.children[1])
            if node.value == "==":
                return left == right
            elif node.value == "!=":
                return left != right
            elif node.value == "<":
                return left < right
            elif node.value == "<=":
                return left <= right
            elif node.value == ">":
                return left > right
            elif node.value == ">=":
                return left >= right
        elif node.node_type == "if_else":
            condition = self.interpret(node.children[0])
            if condition:
                return self.interpret(node.children[1])
            elif len(node.children) > 2 and node.children[2]:
                return self.interpret(node.children[2])
        elif node.node_type == "assignment":
            value = self.interpret(node.children[0])
            self.variables[node.value] = value
        elif node.node_type == "block":
            for statement in node.children:
                self.interpret(statement)
# Compiler class





# Tkinter setup
def run_interpreter():
    source_code = code_input.get("1.0", tk.END).strip()
    try:
        token_list = lexer(source_code)  # Use manual lexer for interpreter
        parser = Parser(token_list)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        result_output.delete("1.0", tk.END)
        result_output.insert(tk.END, f"Variables: {interpreter.variables}")
    except ValueError as e:
        messagebox.showerror("Interpreter Error", str(e))


## the  compiler extention  starts here 



class PLYLexer:
    def __init__(self):
        self.tokens = ('IF', 'ELSE', 'NUMBER', 'IDENTIFIER', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'EQUALS',
                       'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMPARISON')

    def t_IF(self, t):
        r'\bif\b'
        return t

    def t_ELSE(self, t):
        r'\belse\b'
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        return t

    def t_PLUS(self, t):
        r'\+'
        return t

    def t_MINUS(self, t):
        r'-'
        return t

    def t_MULTIPLY(self, t):
        r'\*'
        return t

    def t_DIVIDE(self, t):
        r'/'
        return t

    def t_EQUALS(self, t):
        r'='
        return t

    def t_LPAREN(self, t):
        r'\('
        return t

    def t_RPAREN(self, t):
        r'\)'
        return t

    def t_LBRACE(self, t):
        r'\{'
        return t

    def t_RBRACE(self, t):
        r'\}'
        return t

    def t_SEMICOLON(self, t):
        r';'
        return t

    def t_COMPARISON(self, t):
        r'==|!=|<=|>=|<|>'
        return t

    def t_error(self, t):
        print(f"Unexpected character: {t.value[0]} at position {t.lexpos}")
        raise ValueError(f"Invalid character: {t.value[0]}")

    t_ignore = ' \t'

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def build(self):
        return lex.lex(module=self)


class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []


class PLYParser:
    def __init__(self):
        self.tokens = ('IF', 'ELSE', 'NUMBER', 'IDENTIFIER', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'EQUALS',
                       'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'SEMICOLON', 'COMPARISON')

    def p_program(self, p):
        '''program : block'''
        p[0] = p[1]

    def p_expression_binop(self, p):
        '''expression : expression PLUS term
                      | expression MINUS term
                      | expression MULTIPLY term
                      | expression DIVIDE term
                      | expression COMPARISON term'''
        p[0] = ASTNode("binary_op", p[2], [p[1], p[3]])

    def p_expression_term(self, p):
        '''expression : term'''
        p[0] = p[1]

    def p_term_number(self, p):
        '''term : NUMBER'''
        p[0] = ASTNode("number", p[1])

    def p_term_identifier(self, p):
        '''term : IDENTIFIER'''
        p[0] = ASTNode("identifier", p[1])

    def p_assignment(self, p):
        '''statement : IDENTIFIER EQUALS expression SEMICOLON'''
        p[0] = ASTNode("assignment", p[1], [p[3]])

    def p_if_statement(self, p):
        '''statement : IF LPAREN expression RPAREN LBRACE block RBRACE
                     | IF LPAREN expression RPAREN LBRACE block RBRACE ELSE LBRACE block RBRACE'''
        if len(p) == 8:
            p[0] = ASTNode("if_else", None, [p[3], p[6]])
        else:
            p[0] = ASTNode("if_else", None, [p[3], p[6], p[10]])

    def p_block(self, p):
        '''block : statement block
                 | statement'''
        if len(p) == 3:
            p[0] = ASTNode("block", None, [p[1]] + p[2].children)
        else:
            p[0] = ASTNode("block", None, [p[1]])

    def p_error(self, p):
        if p:
            print(f"Syntax error at token {p.type}: '{p.value}' at line {p.lineno}")
        else:
            print("Syntax error at EOF")
        raise ValueError("Invalid syntax")

    def build(self):
        return yacc.yacc(module=self)


class Compiler:
    def __init__(self):
        self.bytecode = []
        self.label_count = 0
        self.variables = {}  # To store variable values

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def compile(self, node):
        if node.node_type == "number":
            self.bytecode.append(f"PUSH {node.value}")
        elif node.node_type == "identifier":
            self.bytecode.append(f"LOAD {node.value}")
        elif node.node_type == "binary_op":
            self.compile(node.children[0])  # Left operand
            self.compile(node.children[1])  # Right operand
            op_map = {"+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV"}
            self.bytecode.append(op_map[node.value])
        elif node.node_type == "assignment":
            self.compile(node.children[0])  # Value
            self.bytecode.append(f"STORE {node.value}")
        elif node.node_type == "block":
            for statement in node.children:
                self.compile(statement)

    def execute(self):
        stack = []
        pc = 0  # Program counter
        while pc < len(self.bytecode):
            instruction = self.bytecode[pc].split()
            op = instruction[0]

            if op == "PUSH":
                stack.append(int(instruction[1]))
            elif op == "ADD":
                b, a = stack.pop(), stack.pop()
                stack.append(a + b)
            elif op == "SUB":
                b, a = stack.pop(), stack.pop()
                stack.append(a - b)
            elif op == "MUL":
                b, a = stack.pop(), stack.pop()
                stack.append(a * b)
            elif op == "DIV":
                b, a = stack.pop(), stack.pop()
                stack.append(a // b)  # Integer division
            elif op == "STORE":
                self.variables[instruction[1]] = stack.pop()
            elif op == "LOAD":
                stack.append(self.variables[instruction[1]])

            pc += 1

        return stack[-1] if stack else None  # Return the final result if any

    def save_to_file(self, filename="output.bytecode"):
        with open(filename, "w") as f:
            f.write("\n".join(self.bytecode))


def run_compiler():
    source_code = code_input.get("1.0", tk.END).strip()

    try:
        lexer = PLYLexer().build()
        lexer.input(source_code)
        tokens = []
        token = lexer.token()
        while token:
            tokens.append(token)
            token = lexer.token()

        ply_parser = PLYParser()
        parser = ply_parser.build()
        ast = parser.parse(source_code, lexer=lexer)

        compiler = Compiler()
        compiler.compile(ast)
        compiler.save_to_file()
        result = compiler.execute()  # Execute the bytecode and get the result

        result_output.delete("1.0", tk.END)
        output_message = "Compilation successful. Bytecode saved to 'output.bytecode'."
        if result is not None:
            output_message += f"\nResult: {result}"
        result_output.insert(tk.END, output_message)
    except ValueError as e:
        messagebox.showerror("Compiler Error", str(e))








# Tkinter setup
root = tk.Tk()
root.title("Lexer, Parser, Interpreter, and Compiler")

# Input text box
code_input = tk.Text(root, height=10, width=50)
code_input.pack(pady=10)

# Run interpreter button
run_button = tk.Button(root, text="Run Interpreter", command=run_interpreter)
run_button.pack(pady=5)

# Run compiler button
compile_button = tk.Button(root, text="Run Compiler", command=run_compiler)
compile_button.pack(pady=5)

# Output text box
result_output = tk.Text(root, height=10, width=50)
result_output.pack(pady=10)

root.mainloop()
