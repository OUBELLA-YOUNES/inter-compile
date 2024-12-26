import re
import tkinter as tk
from tkinter import messagebox

# Define tokens
tokens = [
    ("IF", r'\bif\b'),  # Keywords need to be distinct
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

# Lexer
def lexer(source_code):
    token_list = []
    while source_code:
        match = None
        for token_type, regex in tokens:
            regex_match = re.match(regex, source_code)
            if regex_match:
                match = regex_match
                lexeme = match.group(0)
                if token_type != "WHITESPACE":  # Ignore spaces
                    token_list.append((token_type, lexeme))
                source_code = source_code[len(lexeme):]
                break
        if not match:
            raise ValueError(f"Unexpected character: {source_code[0]}")
    return token_list

# AST Node class
class ASTNode:
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []

# Parser class
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

# Interpreter class
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

# GUI with Tkinter
def run_interpreter():
    source_code = code_input.get("1.0", tk.END).strip()
    try:
        token_list = lexer(source_code)
        parser = Parser(token_list)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        result_output.delete("1.0", tk.END)
        result_output.insert(tk.END, f"Variables: {interpreter.variables}")
    except ValueError as e:
        messagebox.showerror("Interpreter Error", str(e))

# Tkinter setup
root = tk.Tk()
root.title("Lexer, Parser, and Interpreter")

# Input text box
code_input = tk.Text(root, height=10, width=50)
code_input.pack(pady=10)

# Run interpreter button
run_button = tk.Button(root, text="Run Interpreter", command=run_interpreter)
run_button.pack(pady=5)

# Output text box
result_output = tk.Text(root, height=10, width=50)
result_output.pack(pady=10)

root.mainloop()
