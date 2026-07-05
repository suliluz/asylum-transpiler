import "std/sys.asy";
import "std/time.asy";

print("Starting timer...\n");
sys_millis();
let start_ms = _sys_time_block[3]; // Just grab lower 8 bits

// Waste some time
let i = 0;
while (i < 200) {
    let j = 0;
    while (j < 200) {
        j++;
    }
    i++;
}

sys_millis();
let end_ms = _sys_time_block[3];
print("Done. Delta (lower 8 bits): ");
print_num(end_ms - start_ms);
print("\n");
