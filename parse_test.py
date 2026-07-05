def _parse_var_decl(children):
    name = children[0].value
    fixed_addr = None
    type_node = None
    expr_node = None
    
    idx = 1
    if idx < len(children) and getattr(children[idx], 'type', None) == 'NUMBER':
        fixed_addr = int(children[idx].value)
        idx += 1
        
    if idx < len(children) and getattr(children[idx], 'data', None) and children[idx].data.startswith('type_'):
        type_node = children[idx]
        idx += 1
        
    if idx < len(children):
        expr_node = children[idx]
        
    return name, fixed_addr, type_node, expr_node

from src.parser import parse
for s in ['let x;', 'let x = 5;', 'let x: int = 5;', 'let x @ 10;', 'let x @ 10 = 5;', 'let x @ 10: int = 5;']:
    t = parse(s).children[0]
    print(s, _parse_var_decl(t.children))
