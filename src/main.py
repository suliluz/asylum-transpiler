import sys
import os
import argparse
import ast as python_ast
from parser import parse
from generator import Generator

def resolve_imports(ast, base_dir, imported):
    new_children = []
    for node in ast.children:
        if hasattr(node, 'data') and node.data == 'import_stmt':
            # import_stmt: "import" ESCAPED_STRING ";"
            import_path = python_ast.literal_eval(node.children[0].value)
            if not import_path.endswith('.asy'):
                import_path += '.asy'
            # First try relative to base_dir
            full_path = os.path.join(base_dir, import_path)
            
            # If not found, try relative to the compiler's location
            if not os.path.exists(full_path):
                compiler_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                fallback_path = os.path.join(compiler_dir, import_path)
                if os.path.exists(fallback_path):
                    full_path = fallback_path
            
            if full_path not in imported:
                imported.add(full_path)
                with open(full_path, 'r') as f:
                    sub_ast = parse(f.read())
                sub_ast = resolve_imports(sub_ast, os.path.dirname(full_path), imported)
                new_children.extend(sub_ast.children)
        else:
            new_children.append(node)
    ast.children = new_children
    return ast

def main():
    arg_parser = argparse.ArgumentParser(description="Asylum to Brainfuck Compiler")
    arg_parser.add_argument("input", help="Input .asy file")
    arg_parser.add_argument("-o", "--output", default="out.bf", help="Output .bf file")
    args = arg_parser.parse_args()
    
    base_dir = os.path.dirname(os.path.abspath(args.input))
    with open(args.input, 'r') as f:
        source = f.read()
        
    print(f"Compiling {args.input}...")
    ast = parse(source)
    ast = resolve_imports(ast, base_dir, set([os.path.abspath(args.input)]))

    
    gen = Generator()
    gen.visit(ast)
    bf_code = gen.generate()
    
    with open(args.output, 'w') as f:
        f.write(bf_code)
        
    print(f"Successfully compiled to {args.output}")

if __name__ == "__main__":
    main()
