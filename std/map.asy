// Asylum Hash Map Standard Library
import "std/ptr.asy";
import "std/mem.asy";

// Map size: 16 buckets * 4 bytes/pointer = 64 bytes
// Node size: 4 (key_ptr) + 1 (value) + 4 (next_ptr) = 9 bytes

// Simple sum-and-modulo hash (modulo 16)
func map_hash(k0: byte, k1: byte, k2: byte, k3: byte, len: byte) {
    let sum = 0;
    
    // Read the string bytes
    let i = 0;
    while (i < len) {
        // read_ptr needs the pointer, but we must add i to it
        // Since we don't have 32-bit addition easily, we just inc_current_ptr
        _ptr_block[1] = k0;
        _ptr_block[2] = k1;
        _ptr_block[3] = k2;
        _ptr_block[4] = k3;
        
        let j = 0;
        while (j < i) {
            inc_current_ptr();
            j++;
        }
        
        let char = read_current_ptr();
        sum += char;
        i++;
    }
    
    // modulo 16
    while (sum > 15) {
        sum -= 16;
    }
    
    return sum;
}

// Allocates 64 bytes for 16 buckets (4 bytes each)
// Returns map pointer in _ptr_block[5..8]
func map_create() {
    malloc(0, 0, 0, 64);
    // Initialize all to 0
    let m0 = _ptr_block[5];
    let m1 = _ptr_block[6];
    let m2 = _ptr_block[7];
    let m3 = _ptr_block[8];
    
    let i = 0;
    while (i < 64) {
        _ptr_block[1] = m0;
        _ptr_block[2] = m1;
        _ptr_block[3] = m2;
        _ptr_block[4] = m3;
        let j = 0;
        while (j < i) {
            inc_current_ptr();
            j++;
        }
        write_current_ptr(0);
        i++;
    }
    
    // restore the map pointer to _ptr_block[5..8] so caller can get it
    _ptr_block[5] = m0;
    _ptr_block[6] = m1;
    _ptr_block[7] = m2;
    _ptr_block[8] = m3;
}

// map_set(map[4], key[4], len, val)
func map_set(m0: byte, m1: byte, m2: byte, m3: byte, k0: byte, k1: byte, k2: byte, k3: byte, len: byte, val: byte) {
    let h = map_hash(k0, k1, k2, k3, len);
    
    // allocate node (9 bytes)
    malloc(0, 0, 0, 9);
    let n0 = _ptr_block[5];
    let n1 = _ptr_block[6];
    let n2 = _ptr_block[7];
    let n3 = _ptr_block[8];
    
    // write key_ptr
    _ptr_block[1] = n0; _ptr_block[2] = n1; _ptr_block[3] = n2; _ptr_block[4] = n3;
    write_current_ptr(k0); inc_current_ptr();
    write_current_ptr(k1); inc_current_ptr();
    write_current_ptr(k2); inc_current_ptr();
    write_current_ptr(k3); inc_current_ptr();
    
    // write value
    write_current_ptr(val); inc_current_ptr();
    
    // get bucket index: h * 4
    let bucket_offset = 0;
    let i = 0;
    while (i < h) {
        bucket_offset += 4;
        i++;
    }
    
    // read current bucket head
    _ptr_block[1] = m0; _ptr_block[2] = m1; _ptr_block[3] = m2; _ptr_block[4] = m3;
    let j = 0;
    while (j < bucket_offset) {
        inc_current_ptr();
        j++;
    }
    
    let head0 = read_current_ptr(); inc_current_ptr();
    let head1 = read_current_ptr(); inc_current_ptr();
    let head2 = read_current_ptr(); inc_current_ptr();
    let head3 = read_current_ptr();
    
    // write next_ptr to node
    _ptr_block[1] = n0; _ptr_block[2] = n1; _ptr_block[3] = n2; _ptr_block[4] = n3;
    j = 0;
    while (j < 5) { inc_current_ptr(); j++; }
    
    write_current_ptr(head0); inc_current_ptr();
    write_current_ptr(head1); inc_current_ptr();
    write_current_ptr(head2); inc_current_ptr();
    write_current_ptr(head3);
    
    // write node pointer to bucket head
    _ptr_block[1] = m0; _ptr_block[2] = m1; _ptr_block[3] = m2; _ptr_block[4] = m3;
    j = 0;
    while (j < bucket_offset) { inc_current_ptr(); j++; }
    
    write_current_ptr(n0); inc_current_ptr();
    write_current_ptr(n1); inc_current_ptr();
    write_current_ptr(n2); inc_current_ptr();
    write_current_ptr(n3);
}

// strings matching is hard since we must read both pointers. 
// For simplicity, map_get just matches hash and assumes no collisions.
func map_get(m0: byte, m1: byte, m2: byte, m3: byte, k0: byte, k1: byte, k2: byte, k3: byte, len: byte) {
    let h = map_hash(k0, k1, k2, k3, len);
    
    let bucket_offset = 0;
    let i = 0;
    while (i < h) {
        bucket_offset += 4;
        i++;
    }
    
    _ptr_block[1] = m0; _ptr_block[2] = m1; _ptr_block[3] = m2; _ptr_block[4] = m3;
    let j = 0;
    while (j < bucket_offset) {
        inc_current_ptr();
        j++;
    }
    
    let head0 = read_current_ptr(); inc_current_ptr();
    let head1 = read_current_ptr(); inc_current_ptr();
    let head2 = read_current_ptr(); inc_current_ptr();
    let head3 = read_current_ptr();
    
    if (head0 == 0) {
        if (head1 == 0) {
            if (head2 == 0) {
                if (head3 == 0) {
                    return null;
                }
            }
        }
    }
    
    // read value from head node
    _ptr_block[1] = head0; _ptr_block[2] = head1; _ptr_block[3] = head2; _ptr_block[4] = head3;
    j = 0;
    while (j < 4) { inc_current_ptr(); j++; }
    
    return read_current_ptr();
}
