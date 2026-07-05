import "std/sys.asy";
import "std/map.asy";

func main() {
    print("starting map_create\n");
    map_create();
    print("map_create done\n");
    
    let m0 = _ptr_block[5];
    let m1 = _ptr_block[6];
    let m2 = _ptr_block[7];
    let m3 = _ptr_block[8];
    
    malloc(0, 0, 0, 1);
    let k0 = _ptr_block[5];
    let k1 = _ptr_block[6];
    let k2 = _ptr_block[7];
    let k3 = _ptr_block[8];
    write_ptr(k0, k1, k2, k3, 65); // "A"
    
    print("starting map_set\n");
    map_set(m0, m1, m2, m3, k0, k1, k2, k3, 1, 99); // set "A" to 99
    print("map_set done\n");
    
    print("starting map_get\n");
    let val = map_get(m0, m1, m2, m3, k0, k1, k2, k3, 1);
    print("map_get done\n");
    
    print(val); // should print 'c' (99)
    print("\n");
}

main();
