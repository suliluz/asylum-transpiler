from memory import MemoryManager

class Generator:
    def __init__(self):
        self.code = []
        self.mem = MemoryManager()
        self.ptr = 1024
        self.functions = {}
        self.function_ids = {}
        self.next_func_id = 1
        self.loop_stack = []
        
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
        self.mem.push_scope()
        main_err = self.mem.alloc('__err_flag')
        main_err_code = self.mem.alloc('__err_code')
        self.clear(main_err)
        self.clear(main_err_code)
        
        for child in node.children:
            self.visit(child)
            
        self.mem.pop_scope()
            
    def visit_import_stmt(self, node):
        # handeled by main.py merging asts
        pass

    def visit_func_decl(self, node):
        name = node.children[0].value
        self.functions[name] = node
        self.function_ids[name] = self.next_func_id
        self.next_func_id += 1
            
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
        
    def _is_less(self, a_addr, b_addr, dest_addr):
        self.clear(dest_addr)
        t0 = self.mem.alloc_temp()
        t1 = self.mem.alloc_temp()
        t2 = self.mem.alloc_temp()
        
        self.copy(a_addr, t0)
        self.copy(b_addr, t1)
        
        self.set_val(t2, 1)
        
        self.move_to(t0)
        self._add('[')
        
        self.move_to(t1)
        self._add('[-')
        
        self.move_to(t0)
        self._add('[-]')
        self.clear(t2)
        
        self.move_to(t1)
        self._add(']')
        
        self.move_to(t0)
        self._add('-]')
        
        self.move_to(t1)
        self._add('[')
        self.move_to(t2)
        self._add('[-]')
        self.set_val(dest_addr, 1)
        
        self.move_to(t1)
        self._add('[-]]')
        
        self.mem.free_temp(t0)
        self.mem.free_temp(t1)
        self.mem.free_temp(t2)

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
            val = int(node.children[0].value)
            self.set_val(dest_addr, val)
        elif node.data == 'null_lit':
            self.clear(dest_addr)
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
            if name in getattr(self, 'function_ids', {}):
                self.set_val(dest_addr, self.function_ids[name])
                return
            src_addr = self.mem.get(name)
            self.copy(src_addr, dest_addr)
        elif node.data == 'add_expr':
            self.eval_expr(node.children[0], dest_addr)
            idx = 1
            while idx < len(node.children):
                op = node.children[idx].value
                right = node.children[idx+1]
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
                idx += 2
        elif node.data == 'mul_expr':
            self.eval_expr(node.children[0], dest_addr)
            idx = 1
            while idx < len(node.children):
                op = node.children[idx].value
                right = node.children[idx+1]
                
                temp = self.mem.alloc_temp()
                self.eval_expr(right, temp)
                
                if op == '*':
                    res = self.mem.alloc_temp()
                    self.clear(res)
                    a_copy = self.mem.alloc_temp()
                    self.clear(a_copy)
                    
                    self.move_to(dest_addr)
                    self._add('[-')
                    self.move_to(a_copy)
                    self._add('+')
                    self.move_to(dest_addr)
                    self._add(']')
                    
                    self.move_to(a_copy)
                    self._add('[-')
                    
                    t_copy = self.mem.alloc_temp()
                    self.copy(temp, t_copy)
                    self.move_to(t_copy)
                    self._add('[-')
                    self.move_to(res)
                    self._add('+')
                    self.move_to(t_copy)
                    self._add(']')
                    self.mem.free_temp(t_copy)
                    
                    self.move_to(a_copy)
                    self._add(']')
                    
                    self.copy(res, dest_addr)
                    self.clear(res)
                    self.mem.free_temp(res)
                    self.mem.free_temp(a_copy)
                elif op in ('/', '%'):
                    is_zero = self.mem.alloc_temp()
                    self.set_val(is_zero, 1)
                    t_copy = self.mem.alloc_temp()
                    self.copy(temp, t_copy)
                    self.move_to(t_copy)
                    self._add('[-')
                    self.clear(is_zero)
                    self.move_to(t_copy)
                    self._add(']')
                    self.mem.free_temp(t_copy)
                    
                    self.move_to(is_zero)
                    self._add('[')
                    self.set_val(self.mem.get('__err_flag'), 1)
                    self.set_val(self.mem.get('__err_code'), 1)
                    err_msg = "Math Error: Divide by Zero\n"
                    for c in err_msg:
                        char_val = ord(c)
                        t_char = self.mem.alloc_temp()
                        self.set_val(t_char, char_val)
                        self.move_to(t_char)
                        self._add('.')
                        self.clear(t_char)
                        self.mem.free_temp(t_char)
                    self.clear(is_zero)
                    self._add(']')
                    self.mem.free_temp(is_zero)
                    
                    res = self.mem.alloc_temp()
                    self.clear(res)
                    rem = self.mem.alloc_temp()
                    self.clear(rem)
                    x_copy = self.mem.alloc_temp()
                    self.clear(x_copy)
                    
                    self.move_to(dest_addr)
                    self._add('[-')
                    self.move_to(x_copy)
                    self._add('+')
                    self.move_to(dest_addr)
                    self._add(']')
                    
                    self.move_to(x_copy)
                    self._add('[-')
                    self.move_to(rem)
                    self._add('+')
                    
                    t1 = self.mem.alloc_temp()
                    t2 = self.mem.alloc_temp()
                    self.copy(rem, t1)
                    
                    self.move_to(temp)
                    self._add('[-')
                    self.move_to(t1)
                    self._add('-')
                    self.move_to(t2)
                    self._add('+')
                    self.move_to(temp)
                    self._add(']')
                    
                    self.move_to(t2)
                    self._add('[-')
                    self.move_to(temp)
                    self._add('+')
                    self.move_to(t2)
                    self._add(']')
                    
                    is_eq = self.mem.alloc_temp()
                    self.set_val(is_eq, 1)
                    self.move_to(t1)
                    self._add('[-')
                    self.clear(is_eq)
                    self.move_to(t1)
                    self._add(']')
                    
                    self.move_to(is_eq)
                    self._add('[-')
                    self.move_to(res)
                    self._add('+')
                    self.clear(rem)
                    self.move_to(is_eq)
                    self._add(']')
                    
                    self.mem.free_temp(t1)
                    self.mem.free_temp(t2)
                    self.mem.free_temp(is_eq)
                    
                    self.move_to(x_copy)
                    self._add(']')
                    
                    if op == '/':
                        self.copy(res, dest_addr)
                    else:
                        self.copy(rem, dest_addr)
                        
                    self.clear(res)
                    self.clear(rem)
                    self.clear(x_copy)
                    self.mem.free_temp(res)
                    self.mem.free_temp(rem)
                    self.mem.free_temp(x_copy)
                self.mem.free_temp(temp)
                idx += 2
        elif node.data == 'pow_expr':
            self.eval_expr(node.children[0], dest_addr)
            idx = 1
            while idx < len(node.children):
                op = node.children[idx].value
                right = node.children[idx+1]
                
                temp_base = self.mem.alloc_temp()
                self.copy(dest_addr, temp_base)
                
                temp_exp = self.mem.alloc_temp()
                self.eval_expr(right, temp_exp)
                
                # Check if exp is 0. If so, res is 1. We just loop exp times.
                self.set_val(dest_addr, 1)
                
                self.move_to(temp_exp)
                self._add('[-')
                
                res = self.mem.alloc_temp()
                self.clear(res)
                a_copy = self.mem.alloc_temp()
                self.clear(a_copy)
                
                # dest_addr contains current running product
                self.move_to(dest_addr)
                self._add('[-')
                self.move_to(a_copy)
                self._add('+')
                self.move_to(dest_addr)
                self._add(']')
                
                # Multiply a_copy by temp_base, add to res
                self.move_to(a_copy)
                self._add('[-')
                
                t_base_copy = self.mem.alloc_temp()
                self.copy(temp_base, t_base_copy)
                self.move_to(t_base_copy)
                self._add('[-')
                self.move_to(res)
                self._add('+')
                self.move_to(t_base_copy)
                self._add(']')
                self.mem.free_temp(t_base_copy)
                
                self.move_to(a_copy)
                self._add(']')
                
                self.copy(res, dest_addr)
                self.clear(res)
                self.mem.free_temp(res)
                self.mem.free_temp(a_copy)
                
                self.move_to(temp_exp)
                self._add(']')
                
                self.clear(temp_base)
                self.mem.free_temp(temp_base)
                self.mem.free_temp(temp_exp)
                idx += 2
        elif node.data == 'equality':
            left = node.children[0]
            op = node.children[1].value
            right = node.children[2]
            
            l_addr = self.mem.alloc_temp()
            r_addr = self.mem.alloc_temp()
            self.eval_expr(left, l_addr)
            self.eval_expr(right, r_addr)
            
            if op == '<':
                self._is_less(l_addr, r_addr, dest_addr)
                self.clear(l_addr)
                self.clear(r_addr)
                self.mem.free_temp(l_addr)
                self.mem.free_temp(r_addr)
                return
            elif op == '>':
                self._is_less(r_addr, l_addr, dest_addr)
                self.clear(l_addr)
                self.clear(r_addr)
                self.mem.free_temp(l_addr)
                self.mem.free_temp(r_addr)
                return
                
            self.copy(l_addr, dest_addr)
            temp = self.mem.alloc_temp()
            self.copy(r_addr, temp)
            self.clear(l_addr)
            self.clear(r_addr)
            self.mem.free_temp(l_addr)
            self.mem.free_temp(r_addr)
                
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
                pass

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
                self._generate_inline_call(func_name, node, dest_addr)
            else:
                # Is it a callback?
                try:
                    cb_addr = self.mem.get(func_name)
                except:
                    raise Exception(f"Function {func_name} not found")
                
                args = node.children[1].children if len(node.children) > 1 else []
                cb_val_t = self.mem.alloc_temp()
                if isinstance(cb_addr, tuple):
                    self.copy(cb_addr[0], cb_val_t)
                else:
                    self.copy(cb_addr, cb_val_t)
                
                # Check all functions that match argument length
                for fname, fnode in self.functions.items():
                    params = []
                    for child in fnode.children[1:]:
                        if hasattr(child, 'data') and child.data == 'param_list':
                            params = child.children
                    
                    if len(params) == len(args):
                        fid = self.function_ids[fname]
                        cond = self.mem.alloc_temp()
                        self.copy(cb_val_t, cond)
                        self.move_to(cond)
                        self._add('-' * fid)
                        
                        # if cond == 0, we found it!
                        is_eq = self.mem.alloc_temp()
                        self.set_val(is_eq, 1)
                        self.move_to(cond)
                        self._add('[')
                        self.set_val(is_eq, 0)
                        self.clear(cond)
                        self.move_to(cond)
                        self._add(']')
                        
                        self.move_to(is_eq)
                        self._add('[')
                        
                        # Generate the call
                        self._generate_inline_call(fname, node, dest_addr)
                        
                        self.clear(is_eq)
                        self.move_to(is_eq)
                        self._add(']')
                        self.mem.free_temp(cond)
                        self.mem.free_temp(is_eq)
                        
                self.mem.free_temp(cb_val_t)
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
        
        run_flag = self.mem.alloc_temp()
        self.set_val(run_flag, 1)
        self.loop_stack.append({'run_flag': run_flag, 'cond': cond_temp})
        
        self.mem.push_scope()
        self.visit(block_node)
        self.mem.pop_scope()
        
        self.loop_stack.pop()
        self.clear(run_flag)
        self.mem.free_temp(run_flag)
        
        # Only re-evaluate cond if it was not cleared by break
        t_check = self.mem.alloc_temp()
        self.copy(cond_temp, t_check)
        self.move_to(t_check)
        self._add('[')
        self.clear(cond_temp)
        self.eval_expr(expr_node, cond_temp)
        self.clear(t_check)
        self._add(']')
        self.mem.free_temp(t_check)
        
        self.move_to(cond_temp)
        self._add(']')
        self.mem.free_temp(cond_temp)

    def visit_for_stmt(self, node):
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
        
        run_flag = self.mem.alloc_temp()
        self.set_val(run_flag, 1)
        self.loop_stack.append({'run_flag': run_flag, 'cond': cond_temp})
        
        self.mem.push_scope()
        self.visit(block)
        self.mem.pop_scope()
        
        self.loop_stack.pop()
        
        # Only execute iter_node and re-eval if we didn't break
        t_check = self.mem.alloc_temp()
        self.copy(cond_temp, t_check)
        self.move_to(t_check)
        self._add('[')
        
        if iter_node:
            self.visit(iter_node)
            
        self.clear(cond_temp)
        self.eval_expr(cond_node, cond_temp)
        
        self.clear(t_check)
        self._add(']')
        self.mem.free_temp(t_check)
        
        self.clear(run_flag)
        self.mem.free_temp(run_flag)
        
        self.move_to(cond_temp)
        self._add(']')
        self.mem.free_temp(cond_temp)
        
        self.mem.pop_scope()

    def visit_break_stmt(self, node):
        if not self.loop_stack:
            raise Exception("Break outside loop")
        ctx = self.loop_stack[-1]
        self.clear(ctx['run_flag'])
        self.clear(ctx['cond'])

    def visit_continue_stmt(self, node):
        if not self.loop_stack:
            raise Exception("Continue outside loop")
        ctx = self.loop_stack[-1]
        self.clear(ctx['run_flag'])

    def visit_throw_stmt(self, node):
        expr = node.children[0]
        err_code_temp = self.mem.alloc_temp()
        self.eval_expr(expr, err_code_temp)
        self.set_val(self.mem.get('__err_flag'), 1)
        self.clear(self.mem.get('__err_code'))
        self.copy(err_code_temp, self.mem.get('__err_code'))
        self.clear(err_code_temp)
        self.mem.free_temp(err_code_temp)

    def visit_try_stmt(self, node):
        try_block = node.children[0]
        err_var_name = node.children[1].value
        catch_block = node.children[2]

        self.visit(try_block)

        # Catch
        err_check = self.mem.alloc_temp()
        self.copy(1, err_check)
        self.move_to(err_check)
        self._add('[')
        
        self.clear(1) # Clear error flag
        self.mem.push_scope()
        err_var_addr = self.mem.alloc(err_var_name)
        self.clear(err_var_addr)
        self.copy(2, err_var_addr) # Copy error code
        
        self.visit(catch_block)
        
        self.mem.pop_scope()
        
        self.clear(err_check)
        self._add(']')
        self.mem.free_temp(err_check)

    def visit_block(self, node):
        for stmt in node.children:
            not_err = self.mem.alloc_temp()
            self.set_val(not_err, 1)
            err_copy = self.mem.alloc_temp()
            self.copy(self.mem.get('__err_flag'), err_copy)
            self.move_to(err_copy)
            self._add('[-')
            self.clear(not_err)
            self.move_to(err_copy)
            self._add(']')
            self.mem.free_temp(err_copy)
            
            run_flag_copy = None
            if self.loop_stack:
                run_flag_copy = self.mem.alloc_temp()
                self.copy(self.loop_stack[-1]['run_flag'], run_flag_copy)
            
            self.move_to(not_err)
            self._add('[')
            if run_flag_copy:
                self.move_to(run_flag_copy)
                self._add('[')
                
            self.visit(stmt)
            
            if run_flag_copy:
                self.clear(run_flag_copy)
                self._add(']')
                self.mem.free_temp(run_flag_copy)
                
            self.clear(not_err)
            self._add(']')
            self.mem.free_temp(not_err)

    def generate(self):
        raw = "".join(self.code)
        return raw

    def _generate_inline_call(self, func_name, node, dest_addr):
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
            
        caller_err = self.mem.get('__err_flag')
        caller_err_code = self.mem.get('__err_code')
        self.mem.push_scope()
        callee_err = self.mem.alloc('__err_flag')
        callee_err_code = self.mem.alloc('__err_code')
        self.clear(callee_err)
        self.clear(callee_err_code)
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
            if dest_addr:
                self.copy(ret_addr, dest_addr)
        except:
            pass
            
        callee_err = self.mem.get('__err_flag')
        callee_err_code = self.mem.get('__err_code')
        
        # We need to propagate error up!
        self.copy(callee_err, caller_err)
        self.copy(callee_err_code, caller_err_code)
            
        self.mem.pop_scope()
        for t in arg_temps:
            self.clear(t)
            self.mem.free_temp(t)
