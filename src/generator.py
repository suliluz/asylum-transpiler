from memory import MemoryManager

class Generator:
    def __init__(self):
        self.code = []
        self.mem = MemoryManager()
        self.ptr = 1024
        self.functions = {}
        
    def _add(self, ops):
        self.code.append(ops)
        
    def move_to(self, addr):
        diff = addr - self.ptr
        if diff > 0:
            self._add('>' * diff)
        elif diff < 0:
            self._add('<' * (-diff))
        self.ptr = addr
        
    def clear(self, addr):
        self.move_to(addr)
        self._add('[-]')
        
    def copy(self, src_addr, dest_addr):
        if src_addr == dest_addr:
            return
            
        temp = self.mem.alloc_temp()
        self.clear(dest_addr)
        self.clear(temp)
        
        self.move_to(src_addr)
        self._add('[-')
        self.move_to(dest_addr)
        self._add('+')
        self.move_to(temp)
        self._add('+')
        self.move_to(src_addr)
        self._add(']')
        
        self.move_to(temp)
        self._add('[-')
        self.move_to(src_addr)
        self._add('+')
        self.move_to(temp)
        self._add(']')
        self.mem.free_temp(temp)
        
    def add_val(self, dest_addr, val):
        self.move_to(dest_addr)
        if val > 0:
            self._add('+' * val)
        elif val < 0:
            self._add('-' * (-val))
            
    def set_val(self, dest_addr, val):
        self.clear(dest_addr)
        self.add_val(dest_addr, val)
        
    def visit(self, node):
        if not hasattr(node, 'data'):
            return node.value
            
        method_name = f'visit_{node.data}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)
        else:
            raise Exception(f"No visit method for {node.data}")
            
    def visit_start(self, node):
        for child in node.children:
            self.visit(child)
            
    def visit_import_stmt(self, node):
        # handeled by main.py merging asts
        pass

    def visit_func_decl(self, node):
        name = node.children[0].value
        self.functions[name] = node
            
    def visit_var_decl(self, node):
        name = node.children[0].value
        fixed_addr = None
        type_node = None
        expr_node = None
        
        idx = 1
        if idx < len(node.children) and getattr(node.children[idx], 'type', None) == 'NUMBER':
            fixed_addr = int(node.children[idx].value)
            idx += 1
            
        if idx < len(node.children) and getattr(node.children[idx], 'data', None) and node.children[idx].data.startswith('type_'):
            type_node = node.children[idx]
            idx += 1
            
        if idx < len(node.children):
            expr_node = node.children[idx]
                
        if type_node and type_node.data == 'type_array':
            size = int(type_node.children[1].value)
            addr, _ = self.mem.alloc_array(name, size, fixed_addr=fixed_addr)
            if expr_node:
                # check if expr is just a string atom
                if getattr(expr_node, 'data', None) == 'string' or (getattr(expr_node, 'children', None) and getattr(expr_node.children[0], 'data', None) == 'string'):
                    import ast
                    # find the string node
                    str_node = expr_node
                    while str_node.data != 'string':
                        str_node = str_node.children[0]
                    val = ast.literal_eval(str_node.children[0].value)
                    for i, char in enumerate(val[:size]):
                        self.set_val(addr + i, ord(char))
                else:
                    self.eval_expr(expr_node, addr)
        else:
            json_node = expr_node
            while json_node and hasattr(json_node, 'data') and json_node.data != 'json_obj':
                if len(json_node.children) == 1:
                    json_node = json_node.children[0]
                else:
                    json_node = None
                    
            if json_node and hasattr(json_node, 'data') and json_node.data == 'json_obj':
                import ast
                fields = []
                values = []
                for pair in json_node.children:
                    key = ast.literal_eval(pair.children[0].value)
                    fields.append(key)
                    values.append(pair.children[1])
                base_addr, layout = self.mem.alloc_struct(name, fields, fixed_addr=fixed_addr)
                for key, val_expr in zip(fields, values):
                    self.eval_expr(val_expr, base_addr + layout[key])
            else:
                addr = self.mem.alloc(name, fixed_addr=fixed_addr)
                if expr_node:
                    self.eval_expr(expr_node, addr)
                elif fixed_addr is None:
                    self.clear(addr)
                
    def visit_inc(self, node):
        name = node.children[0].value
        addr = self.mem.get(name)
        if isinstance(addr, tuple): addr = addr[0]
        self.move_to(addr)
        self._add('+')
        
    def visit_dec(self, node):
        name = node.children[0].value
        addr = self.mem.get(name)
        if isinstance(addr, tuple): addr = addr[0]
        self.move_to(addr)
        self._add('-')
        
    def visit_assign_add(self, node):
        name = node.children[0].value
        expr_node = node.children[1]
        addr = self.mem.get(name)
        if isinstance(addr, tuple): addr = addr[0]
        temp = self.mem.alloc_temp()
        self.eval_expr(expr_node, temp)
        self.move_to(temp)
        self._add('[-')
        self.move_to(addr)
        self._add('+')
        self.move_to(temp)
        self._add(']')
        self.mem.free_temp(temp)
        
    def visit_assign_sub(self, node):
        name = node.children[0].value
        expr_node = node.children[1]
        addr = self.mem.get(name)
        if isinstance(addr, tuple): addr = addr[0]
        temp = self.mem.alloc_temp()
        self.eval_expr(expr_node, temp)
        self.move_to(temp)
        self._add('[-')
        self.move_to(addr)
        self._add('-')
        self.move_to(temp)
        self._add(']')
        self.mem.free_temp(temp)

    def visit_assignment(self, node):
        if hasattr(node, 'data') and node.data == 'assign_add':
            return self.visit_assign_add(node)
        if hasattr(node, 'data') and node.data == 'assign_sub':
            return self.visit_assign_sub(node)
            
        if hasattr(node.children[0], 'data') and node.children[0].data == 'prop_access':
            prop_access = node.children[0]
            expr_node = node.children[1]
            name = prop_access.children[0].value
            prop = prop_access.children[1].value
            base_addr_tuple = self.mem.get(name)
            if not isinstance(base_addr_tuple, tuple) or not isinstance(base_addr_tuple[1], dict):
                raise Exception(f"{name} is not an object")
            base_addr, layout = base_addr_tuple
            if prop not in layout:
                raise Exception(f"Property {prop} does not exist on {name}")
            dest_addr = base_addr + layout[prop]
            self.eval_expr(expr_node, dest_addr)
            return

        if hasattr(node.children[0], 'data') and node.children[0].data == 'array_access':
            arr_access = node.children[0]
            expr_node = node.children[1]
            
            name = arr_access.children[0].value
            index_expr = arr_access.children[1]
            base_addr_tuple = self.mem.get(name)
            if not isinstance(base_addr_tuple, tuple):
                raise Exception(f"{name} is not an array")
            base_addr, size = base_addr_tuple
            
            if expr_node.data == 'string' and index_expr.data == 'number':
                import ast
                start_idx = int(index_expr.children[0].value)
                val = ast.literal_eval(expr_node.children[0].value) + '\0'
                for i, char in enumerate(val):
                    if start_idx + i < size:
                        addr = base_addr + start_idx + i
                        self.set_val(addr, ord(char))
                return
            
            val_temp = self.mem.alloc_temp()
            self.eval_expr(expr_node, val_temp)
            
            if index_expr.data == 'number':
                offset = int(index_expr.children[0].value)
                if offset < size:
                    dest_addr = base_addr + offset
                    self.clear(dest_addr)
                    self.copy(val_temp, dest_addr)
                self.clear(val_temp)
                self.mem.free_temp(val_temp)
                return
            
            idx_temp = self.mem.alloc_temp()
            self.eval_expr(index_expr, idx_temp)
            
            for offset in range(size):
                t0 = self.mem.alloc_temp()
                t1 = self.mem.alloc_temp()
                
                self.copy(idx_temp, t0)
                self.add_val(t0, -offset)
                
                self.set_val(t1, 1)
                self.move_to(t0)
                self._add('[')
                self.clear(t1)
                self.clear(t0)
                self._add(']')
                
                self.move_to(t1)
                self._add('[')
                self.copy(val_temp, base_addr + offset)
                self.clear(t1)
                self._add(']')
                
                self.mem.free_temp(t0)
                self.mem.free_temp(t1)
                
            self.clear(idx_temp)
            self.clear(val_temp)
            self.mem.free_temp(idx_temp)
            self.mem.free_temp(val_temp)
        else:
            name = node.children[0].value
            expr_node = node.children[1]
            addr = self.mem.get(name)
            self.eval_expr(expr_node, addr)
        
    def _do_print(self, arg):
        if arg.data == 'string':
            import ast
            val = ast.literal_eval(arg.children[0].value)
            temp = self.mem.alloc_temp()
            self.clear(temp)
            last_val = 0
            for char in val:
                c_val = ord(char)
                self.add_val(temp, c_val - last_val)
                self.move_to(temp)
                self._add('.')
                last_val = c_val
            self.clear(temp)
            self.mem.free_temp(temp)
        else:
            temp = self.mem.alloc_temp()
            self.eval_expr(arg, temp)
            self.move_to(temp)
            self._add('.')
            self.clear(temp)
            self.mem.free_temp(temp)

    def eval_expr(self, node, dest_addr):
        if node.data == 'number':
            val = int(float(node.children[0].value))
            self.set_val(dest_addr, val)
        elif node.data == 'string':
            import ast
            val = ast.literal_eval(node.children[0].value)
            self.set_val(dest_addr, ord(val[0]) if val else 0)
        elif node.data == 'prop_access':
            name = node.children[0].value
            prop = node.children[1].value
            base_addr_tuple = self.mem.get(name)
            if not isinstance(base_addr_tuple, tuple) or not isinstance(base_addr_tuple[1], dict):
                raise Exception(f"{name} is not an object")
            base_addr, layout = base_addr_tuple
            if prop not in layout:
                raise Exception(f"Property {prop} does not exist on {name}")
            src_addr = base_addr + layout[prop]
            self.clear(dest_addr)
            self.copy(src_addr, dest_addr)
        elif node.data == 'array_access':
            name = node.children[0].value
            index_expr = node.children[1]
            base_addr_tuple = self.mem.get(name)
            if not isinstance(base_addr_tuple, tuple):
                raise Exception(f"{name} is not an array")
            base_addr, size = base_addr_tuple
            
            if index_expr.data == 'number':
                offset = int(index_expr.children[0].value)
                if offset < size:
                    src_addr = base_addr + offset
                    self.copy(src_addr, dest_addr)
                else:
                    self.clear(dest_addr)
                return
            
            idx_temp = self.mem.alloc_temp()
            self.eval_expr(index_expr, idx_temp)
            
            self.clear(dest_addr)
            
            for offset in range(size):
                t0 = self.mem.alloc_temp()
                t1 = self.mem.alloc_temp()
                
                self.copy(idx_temp, t0)
                self.add_val(t0, -offset)
                
                self.set_val(t1, 1)
                self.move_to(t0)
                self._add('[')
                self.clear(t1)
                self.clear(t0)
                self._add(']')
                
                self.move_to(t1)
                self._add('[')
                self.copy(base_addr + offset, dest_addr)
                self.clear(t1)
                self._add(']')
                
                self.mem.free_temp(t0)
                self.mem.free_temp(t1)
                
            self.clear(idx_temp)
            self.mem.free_temp(idx_temp)
        elif node.data == 'var':
            name = node.children[0].value
            src_addr = self.mem.get(name)
            self.copy(src_addr, dest_addr)
        elif node.data == 'add_expr':
            left = node.children[0]
            op = node.children[1].value
            right = node.children[2]
            
            self.eval_expr(left, dest_addr)
            temp = self.mem.alloc_temp()
            self.eval_expr(right, temp)
            
            self.move_to(temp)
            self._add('[-')
            self.move_to(dest_addr)
            if op == '+':
                self._add('+')
            else:
                self._add('-')
            self.move_to(temp)
            self._add(']')
            self.mem.free_temp(temp)
        elif node.data == 'equality':
            left = node.children[0]
            op = node.children[1].value
            right = node.children[2]
            
            self.eval_expr(left, dest_addr)
            temp = self.mem.alloc_temp()
            self.eval_expr(right, temp)
            
            self.move_to(temp)
            self._add('[-')
            self.move_to(dest_addr)
            self._add('-')
            self.move_to(temp)
            self._add(']')
            self.mem.free_temp(temp)
            
            if op == '==':
                t0 = self.mem.alloc_temp()
                t1 = self.mem.alloc_temp()
                self.set_val(t0, 0)
                self.set_val(t1, 1)
                
                self.move_to(dest_addr)
                self._add('[')
                self.clear(t1)
                self.clear(dest_addr)
                self._add(']')
                
                self.copy(t1, dest_addr)
                self.clear(t1)
                self.mem.free_temp(t0)
                self.mem.free_temp(t1)
            elif op == '!=':
                t1 = self.mem.alloc_temp()
                self.set_val(t1, 0)
                self.move_to(dest_addr)
                self._add('[')
                self.set_val(t1, 1)
                self.clear(dest_addr)
                self._add(']')
                self.copy(t1, dest_addr)
                self.clear(t1)
                self.mem.free_temp(t1)
            else:
                raise Exception(f"Op {op} not implemented fully yet")

        elif node.data == 'func_call':
            func_name = node.children[0].value
            if func_name == 'print':
                arg = node.children[1].children[0]
                self._do_print(arg)
            elif func_name == 'read':
                self.move_to(dest_addr)
                self._add(',')
            elif func_name == 'syscall':
                arg_name = node.children[1].children[0].children[0].value
                addr = self.mem.get(arg_name)
                if isinstance(addr, tuple):
                    addr = addr[0]
                self.move_to(addr)
                self._add('#')
                self.copy(addr, dest_addr)
            elif func_name in self.functions:
                func_node = self.functions[func_name]
                args = node.children[1].children if len(node.children) > 1 else []
                params = []
                block = None
                for child in func_node.children[1:]:
                    if hasattr(child, 'data') and child.data == 'param_list':
                        params = child.children
                    if hasattr(child, 'data') and child.data == 'block':
                        block = child
                        
                if len(args) != len(params):
                    raise Exception(f"Func {func_name} expects {len(params)} args, got {len(args)}")
                    
                arg_temps = []
                for arg in args:
                    t = self.mem.alloc_temp()
                    self.eval_expr(arg, t)
                    arg_temps.append(t)
                    
                self.mem.push_scope()
                ret_addr = self.mem.alloc('_return')
                self.clear(ret_addr)
                
                for i, param in enumerate(params):
                    p_name = param.children[0].value
                    p_addr = self.mem.alloc(p_name)
                    self.clear(p_addr)
                    self.copy(arg_temps[i], p_addr)
                    
                self.visit(block)
                
                try:
                    ret_addr = self.mem.get('_return')
                    self.copy(ret_addr, dest_addr)
                except:
                    pass
                    
                self.mem.pop_scope()
                for t in arg_temps:
                    self.clear(t)
                    self.mem.free_temp(t)
            else:
                raise Exception(f"Function {func_name} not found")
        else:
            raise Exception(f"Unsupported expr {node.data}")
            
    def visit_return_stmt(self, node):
        expr = node.children[0]
        try:
            ret_addr = self.mem.get('_return')
        except:
            raise Exception("Cannot return outside of function")
        
        self.clear(ret_addr)
        self.eval_expr(expr, ret_addr)

    def visit_expr_stmt(self, node):
        expr = node.children[0]
        if expr.data == 'func_call':
            func_name = expr.children[0].value
            if func_name == 'print':
                arg_list = expr.children[1]
                arg = arg_list.children[0] if arg_list.children else None
                if arg:
                    self._do_print(arg)
            elif func_name == 'syscall':
                arg_name = expr.children[1].children[0].children[0].value
                addr = self.mem.get(arg_name)
                if isinstance(addr, tuple):
                    addr = addr[0]
                self.move_to(addr)
                self._add('#')
            else:
                t = self.mem.alloc_temp()
                self.eval_expr(expr, t)
                self.clear(t)
                self.mem.free_temp(t)
        elif expr.data == 'inc':
            self.visit_inc(expr)
        elif expr.data == 'dec':
            self.visit_dec(expr)
        else:
            t = self.mem.alloc_temp()
            self.eval_expr(expr, t)
            self.clear(t)
            self.mem.free_temp(t)

    def visit_if_stmt(self, node):
        expr_node = node.children[0]
        block_node = node.children[1]
        else_block = node.children[2] if len(node.children) > 2 else None
        
        cond_temp = self.mem.alloc_temp()
        flag_temp = self.mem.alloc_temp()
        
        self.eval_expr(expr_node, cond_temp)
        
        self.set_val(flag_temp, 1)
        
        self.move_to(cond_temp)
        self._add('[')
        
        self.mem.push_scope()
        self.visit(block_node)
        self.mem.pop_scope()
        
        self.clear(flag_temp)
        self.clear(cond_temp)
        self._add(']')
        
        if else_block:
            self.move_to(flag_temp)
            self._add('[')
            self.mem.push_scope()
            self.visit(else_block)
            self.mem.pop_scope()
            self.clear(flag_temp)
            self._add(']')
            
        self.mem.free_temp(flag_temp)
        self.mem.free_temp(cond_temp)
        
    def visit_while_stmt(self, node):
        expr_node = node.children[0]
        block_node = node.children[1]
        
        cond_temp = self.mem.alloc_temp()
        self.eval_expr(expr_node, cond_temp)
        
        self.move_to(cond_temp)
        self._add('[')
        
        self.mem.push_scope()
        self.visit(block_node)
        self.mem.pop_scope()
        
        self.eval_expr(expr_node, cond_temp)
        self.move_to(cond_temp)
        self._add(']')
        self.mem.free_temp(cond_temp)

    def visit_for_stmt(self, node):
        # for_stmt: "for" "(" (var_decl | assignment)? expr ";" (assignment | inc_dec_stmt)? ")" block
        # Children could be: [init, cond, iter, block] or [cond, iter, block] or [init, cond, block] or [cond, block]
        # Let's dynamically find them by looking at data or assuming last is block, second to last could be iter...
        # Actually it's better to check the node tree.
        # Lark drops empty optionals, but let's be careful.
        
        block = node.children[-1]
        
        # Determine components
        init_node = None
        cond_node = None
        iter_node = None
        
        if len(node.children) == 4:
            init_node = node.children[0]
            cond_node = node.children[1]
            iter_node = node.children[2]
        elif len(node.children) == 3:
            # could be init + cond + block, or cond + iter + block
            if getattr(node.children[0], 'data', None) in ('var_decl', 'assignment'):
                init_node = node.children[0]
                cond_node = node.children[1]
            else:
                cond_node = node.children[0]
                iter_node = node.children[1]
        elif len(node.children) == 2:
            cond_node = node.children[0]
            
        self.mem.push_scope()
        
        if init_node:
            self.visit(init_node)
            
        cond_temp = self.mem.alloc_temp()
        self.eval_expr(cond_node, cond_temp)
        
        self.move_to(cond_temp)
        self._add('[')
        
        self.mem.push_scope()
        self.visit(block)
        self.mem.pop_scope()
        
        if iter_node:
            self.visit(iter_node)
            
        self.eval_expr(cond_node, cond_temp)
        self.move_to(cond_temp)
        self._add(']')
        self.mem.free_temp(cond_temp)
        
        self.mem.pop_scope()

    def visit_block(self, node):
        for stmt in node.children:
            self.visit(stmt)

    def generate(self):
        raw = "".join(self.code)
        return raw
