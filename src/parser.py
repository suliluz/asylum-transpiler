import os
from lark import Lark

def get_parser():
    grammar_path = os.path.join(os.path.dirname(__file__), 'grammar.lark')
    with open(grammar_path, 'r') as f:
        grammar = f.read()
    return Lark(grammar, parser='lalr', start='start')

def parse(text):
    parser = get_parser()
    return parser.parse(text)

if __name__ == '__main__':
    test_code = """
    let x: byte = 5;
    let y = 10;
    if (x == y) {
        x = x + 1;
    }
    """
    ast = parse(test_code)
    print(ast.pretty())
