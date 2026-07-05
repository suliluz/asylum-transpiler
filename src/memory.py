class MemoryManager:
    def __init__(self):
        self.scopes = [{
            '__err_flag': 1,
            '__err_code': 2
        }]
        self.next_free = 1024
        self.temp_pool = set()
        self.freed_addrs = []
        
    def push_scope(self):
        self.scopes.append({})
        
    def pop_scope(self):
        popped = self.scopes.pop()
        for addr in popped.values():
            if isinstance(addr, tuple) and isinstance(addr[1], dict):
                for offset in addr[1].values():
                    self.freed_addrs.append(addr[0] + offset)
            elif isinstance(addr, tuple):
                for offset in range(addr[1]):
                    self.freed_addrs.append(addr[0] + offset)
            else:
                self.freed_addrs.append(addr)
            
    def alloc(self, name, fixed_addr=None):
        if name in self.scopes[-1]:
            raise Exception(f"Variable {name} already declared in this scope.")
        addr = fixed_addr if fixed_addr is not None else self._get_free_addr()
        self.scopes[-1][name] = addr
        return addr
        
    def alloc_array(self, name, size, fixed_addr=None):
        if name in self.scopes[-1]:
            raise Exception(f"Variable {name} already declared in this scope.")
        base_addr = fixed_addr if fixed_addr is not None else self.next_free
        if fixed_addr is None:
            self.next_free += size
        self.scopes[-1][name] = (base_addr, size)
        return base_addr, size
        
    def alloc_struct(self, name, fields, fixed_addr=None):
        if name in self.scopes[-1]:
            raise Exception(f"Variable {name} already declared in this scope.")
        base_addr = fixed_addr if fixed_addr is not None else self.next_free
        size = len(fields)
        if fixed_addr is None:
            self.next_free += size
        
        layout = {}
        for i, field in enumerate(fields):
            layout[field] = i
            
        self.scopes[-1][name] = (base_addr, layout)
        return base_addr, layout
        
    def get(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Variable {name} not declared.")
        
    def alloc_temp(self):
        addr = self._get_free_addr()
        self.temp_pool.add(addr)
        return addr
        
    def free_temp(self, addr):
        if addr in self.temp_pool:
            self.temp_pool.remove(addr)
            self.freed_addrs.append(addr)
            
    def _get_free_addr(self):
        if self.freed_addrs:
            return self.freed_addrs.pop()
        addr = self.next_free
        self.next_free += 1
        return addr
